"""
RedAmon Agent Orchestrator

Main agent class that orchestrates LangGraph execution with MCP tools
and Neo4j graph database integration.
"""

import os
import re
import logging
from typing import Optional, List
from contextvars import ContextVar

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_neo4j import Neo4jGraph

from state import AgentState, InvokeResponse
from utils import create_config, get_config_values, set_checkpointer
from params import OPENAI_MODEL, MCP_CURL_URL, CREATE_GRAPH_IMAGRE_ON_INIT
from prompts import TEXT_TO_CYPHER_SYSTEM

# Context variables to pass user_id and project_id to tools
_current_user_id: ContextVar[str] = ContextVar('current_user_id', default='')
_current_project_id: ContextVar[str] = ContextVar('current_project_id', default='')

checkpointer = MemorySaver()
set_checkpointer(checkpointer)

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """
    Main orchestrator for the RedAmon agent system.

    Combines:
    - LangGraph for state management and flow control
    - MCP tools (curl) for HTTP requests
    - Neo4j text-to-cypher for graph queries
    - OpenAI GPT-4.1 for reasoning
    - MemorySaver checkpointer for session persistence
    """

    def __init__(self):
        """Initialize the orchestrator with configuration."""
        self.model_name = OPENAI_MODEL
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.neo4j_user = os.getenv("NEO4J_USER", "neo4j")
        self.neo4j_password = os.getenv("NEO4J_PASSWORD")
        self.mcp_curl_url = MCP_CURL_URL

        self.llm: Optional[ChatOpenAI] = None
        self.llm_with_tools: Optional[ChatOpenAI] = None
        self.mcp_client: Optional[MultiServerMCPClient] = None
        self.neo4j_graph: Optional[Neo4jGraph] = None
        self.tools: List = []
        self.graph = None

        self._initialized = False

    async def initialize(self) -> None:
        """
        Initialize all components asynchronously.

        Must be called before invoke().
        """
        if self._initialized:
            logger.warning("Orchestrator already initialized")
            return
        logger.info("Initializing AgentOrchestrator...")

        self._setup_llm()
        await self._setup_mcp_tools()
        self._setup_graph_tools()
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        self._build_graph()
        self._initialized = True

        if CREATE_GRAPH_IMAGRE_ON_INIT:
            self._save_graph_image()

        logger.info(f"AgentOrchestrator initialized with {len(self.tools)} tools")

    def _setup_llm(self) -> None:
        """Initialize the OpenAI LLM."""
        logger.info(f"Setting up LLM: {self.model_name}")
        self.llm = ChatOpenAI(
            model=self.model_name,
            api_key=self.openai_api_key,
            temperature=0
        )

    async def _setup_mcp_tools(self) -> None:
        """
        Connect to MCP servers and load tools.

        Currently connects to curl server via SSE transport.
        """
        logger.info(f"Connecting to MCP curl server at {self.mcp_curl_url}")

        try:
            self.mcp_client = MultiServerMCPClient({
                "curl": {
                    "url": self.mcp_curl_url,
                    "transport": "sse",
                }
            })

            mcp_tools = await self.mcp_client.get_tools()
            self.tools.extend(mcp_tools)
            logger.info(f"Loaded {len(mcp_tools)} tools from MCP server")

        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {e}")
            logger.warning("Continuing without MCP tools")

    def _inject_tenant_filter(self, cypher: str, user_id: str, project_id: str) -> str:
        """
        Inject mandatory user_id and project_id filters into a Cypher query.

        This ensures all queries are scoped to the current user's project,
        preventing cross-tenant data access.

        Args:
            cypher: The AI-generated Cypher query
            user_id: Current user's ID
            project_id: Current project's ID

        Returns:
            Modified Cypher query with tenant filters applied
        """
        # Find all node variable declarations in MATCH clauses
        # Pattern matches: (variable:Label) or (variable:Label {props})
        node_pattern = r'\((\w+):(\w+)(?:\s*\{[^}]*\})?\)'

        # Node types that require tenant filtering (exclude CVE which is global)
        tenant_nodes = {
            'Domain', 'Subdomain', 'IP', 'Port', 'Service', 'BaseURL',
            'Technology', 'Vulnerability', 'Endpoint', 'Parameter',
            'Header', 'DNSRecord', 'Certificate', 'MitreData', 'Capec'
        }

        # Find all node variables that need filtering
        matches = re.findall(node_pattern, cypher)
        filter_vars = []
        for var_name, label in matches:
            if label in tenant_nodes:
                filter_vars.append(var_name)

        if not filter_vars:
            return cypher

        # Build the tenant filter clause
        tenant_conditions = []
        for var in set(filter_vars):  # Use set to avoid duplicates
            tenant_conditions.append(f"{var}.user_id = $tenant_user_id")
            tenant_conditions.append(f"{var}.project_id = $tenant_project_id")

        tenant_filter = " AND ".join(tenant_conditions)

        # Inject the filter into the query
        # If WHERE exists, add to it; otherwise insert WHERE before RETURN/WITH/ORDER/LIMIT
        if re.search(r'\bWHERE\b', cypher, re.IGNORECASE):
            # Add to existing WHERE clause
            cypher = re.sub(
                r'(\bWHERE\b\s+)',
                rf'\1({tenant_filter}) AND ',
                cypher,
                count=1,
                flags=re.IGNORECASE
            )
        else:
            # Insert WHERE before RETURN, WITH, ORDER BY, or LIMIT
            insert_pattern = r'(\s*)(RETURN|WITH|ORDER\s+BY|LIMIT)'
            match = re.search(insert_pattern, cypher, re.IGNORECASE)
            if match:
                insert_pos = match.start()
                cypher = cypher[:insert_pos] + f" WHERE {tenant_filter} " + cypher[insert_pos:]

        return cypher

    def _execute_filtered_query(self, cypher: str, user_id: str, project_id: str) -> str:
        """
        Execute a Cypher query with tenant parameters.

        Args:
            cypher: The Cypher query to execute
            user_id: Current user's ID
            project_id: Current project's ID

        Returns:
            Query results as a string
        """
        try:
            result = self.neo4j_graph.query(
                cypher,
                params={
                    "tenant_user_id": user_id,
                    "tenant_project_id": project_id
                }
            )
            if not result:
                return "No results found"
            return str(result)
        except Exception as e:
            logger.error(f"Query execution error: {e}")
            return f"Error executing query: {str(e)}"

    def _generate_cypher(self, question: str) -> str:
        """
        Use LLM to generate a Cypher query from natural language.

        Args:
            question: Natural language question about the data

        Returns:
            Generated Cypher query string
        """
        schema = self.neo4j_graph.get_schema

        prompt = f"""{TEXT_TO_CYPHER_SYSTEM}

## Current Database Schema
{schema}

## Important
- Generate ONLY the Cypher query, no explanations
- Do NOT include user_id or project_id filters - they will be added automatically
- Always use LIMIT to restrict results

User Question: {question}

Cypher Query:"""

        response = self.llm.invoke(prompt)
        cypher = response.content.strip()

        # Clean up the response - remove markdown code blocks if present
        if cypher.startswith("```"):
            lines = cypher.split("\n")
            cypher = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])

        return cypher.strip()

    def _setup_graph_tools(self) -> None:
        """
        Set up Neo4j text-to-cypher tool with mandatory tenant filtering.

        Creates a tool that:
        1. Converts natural language to Cypher using LLM
        2. Injects mandatory user_id and project_id filters
        3. Executes the filtered query against Neo4j
        """
        logger.info(f"Setting up Neo4j connection to {self.neo4j_uri}")

        try:
            self.neo4j_graph = Neo4jGraph(
                url=self.neo4j_uri,
                username=self.neo4j_user,
                password=self.neo4j_password
            )

            # Store reference to self for use in the tool closure
            orchestrator = self

            @tool
            def query_graph(question: str) -> str:
                """
                Query the Neo4j graph database using natural language.

                Use this tool to retrieve reconnaissance data such as:
                - Domains, subdomains, and their relationships
                - IP addresses and their associated ports/services
                - Technologies detected on targets
                - Vulnerabilities and CVEs found
                - Any other security reconnaissance data

                Args:
                    question: Natural language question about the data

                Returns:
                    Query results as a string
                """
                # Get current user/project from context
                user_id = _current_user_id.get()
                project_id = _current_project_id.get()

                if not user_id or not project_id:
                    return "Error: Missing user_id or project_id context"

                logger.info(f"[{user_id}/{project_id}] Generating Cypher for: {question[:50]}...")

                try:
                    # Step 1: Generate Cypher from natural language
                    cypher = orchestrator._generate_cypher(question)
                    logger.info(f"[{user_id}/{project_id}] Generated Cypher: {cypher}")

                    # Step 2: Inject mandatory tenant filters
                    filtered_cypher = orchestrator._inject_tenant_filter(cypher, user_id, project_id)
                    logger.info(f"[{user_id}/{project_id}] Filtered Cypher: {filtered_cypher}")

                    # Step 3: Execute the filtered query
                    result = orchestrator._execute_filtered_query(filtered_cypher, user_id, project_id)

                    return result

                except Exception as e:
                    logger.error(f"[{user_id}/{project_id}] Query error: {e}")
                    return f"Error querying graph: {str(e)}"

            self.tools.append(query_graph)
            logger.info("Neo4j graph query tool configured with tenant filtering")

        except Exception as e:
            logger.error(f"Failed to set up Neo4j: {e}")
            logger.warning("Continuing without graph query tool")

    def _build_graph(self) -> None:
        """
        Build the LangGraph StateGraph with MemorySaver checkpointer.

        Flow: START -> agent -> tools (conditional) -> response -> END
        The response node generates a natural language answer from tool output.
        The checkpointer automatically handles session persistence.
        """
        logger.info("Building LangGraph StateGraph with MemorySaver checkpointer")

        builder = StateGraph(AgentState)
        builder.add_node("agent", self._agent_node)
        builder.add_node("tools", ToolNode(self.tools))
        builder.add_node("response", self._response_node)

        builder.add_edge(START, "agent")
        builder.add_conditional_edges(
            "agent",
            self._should_use_tool,
            {
                "tools": "tools",
                "end": END
            }
        )
        builder.add_edge("tools", "response")
        builder.add_edge("response", END)

        self.graph = builder.compile(checkpointer=checkpointer)
        logger.info("LangGraph compiled with MemorySaver checkpointer")

    def _save_graph_image(self) -> None:
        """
        Save the LangGraph structure as a PNG image.

        The image is saved to the agentic folder as 'graph_structure.png'.
        Requires pygraphviz or grandalf for rendering.
        """
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            image_path = os.path.join(current_dir, "graph_structure.png")
            png_data = self.graph.get_graph().draw_mermaid_png()

            with open(image_path, "wb") as f:
                f.write(png_data)

            logger.info(f"Graph structure image saved to {image_path}")

        except Exception as e:
            logger.warning(f"Could not save graph image: {e}")

    def _agent_node(self, state: AgentState, config: Optional[dict] = None) -> dict:
        """
        Main reasoning node - LLM decides which tool to use.

        Args:
            state: Current agent state
            config: Contains configurable with user_id, project_id, session_id

        Returns:
            Updated state with LLM response
        """
        config = config or {}
        user_id, project_id, session_id = get_config_values(config)
        logger.info(f"[{user_id}/{project_id}/{session_id}] Agent node processing...")

        response = self.llm_with_tools.invoke(state["messages"])

        logger.debug(f"[{user_id}/{project_id}/{session_id}] LLM response type: {type(response)}")

        if hasattr(response, 'tool_calls') and response.tool_calls:
            tool_name = response.tool_calls[0].get('name', 'unknown')
            logger.info(f"[{user_id}/{project_id}/{session_id}] Tool selected: {tool_name}")

        return {"messages": [response]}

    def _should_use_tool(self, state: AgentState) -> str:
        """
        Determine if we should route to tools or end.

        Args:
            state: Current agent state

        Returns:
            "tools" if tool calls present, "end" otherwise
        """
        last_message = state["messages"][-1]

        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "tools"

        return "end"

    def _response_node(self, state: AgentState, config: Optional[dict] = None) -> dict:
        """
        Response node - generates a natural language answer from tool output.

        This node takes the tool output and asks the LLM to create a
        human-friendly response summarizing the results.

        Args:
            state: Current agent state (contains tool output in messages)
            config: Contains configurable with user_id, project_id, session_id

        Returns:
            Updated state with natural language response
        """
        config = config or {}
        user_id, project_id, session_id = get_config_values(config)
        logger.info(f"[{user_id}/{project_id}/{session_id}] Response node processing...")

        response = self.llm.invoke(state["messages"])

        logger.debug(f"[{user_id}/{project_id}/{session_id}] Generated response")

        return {"messages": [response]}

    async def invoke(
        self,
        question: str,
        user_id: str,
        project_id: str,
        session_id: str
    ) -> InvokeResponse:
        """Main entry point for agent invocation."""
        if not self._initialized:
            raise RuntimeError("Orchestrator not initialized. Call initialize() first.")

        logger.info(f"[{user_id}/{project_id}/{session_id}] Invoking with: {question[:50]}...")

        # Set context variables for tenant filtering in graph queries
        _current_user_id.set(user_id)
        _current_project_id.set(project_id)

        try:
            config = create_config(user_id, project_id, session_id)
            input_data = {
                "messages": [HumanMessage(content=question)]
            }

            final_state = await self.graph.ainvoke(input_data, config)

            tool_used = None
            tool_output = None

            for msg in final_state.get("messages", []):
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    tool_used = msg.tool_calls[0].get('name')
                if hasattr(msg, 'name') and hasattr(msg, 'content'):
                    tool_output = msg.content

            final_answer = ""
            for msg in reversed(final_state.get("messages", [])):
                if isinstance(msg, AIMessage) and not hasattr(msg, 'name'):
                    final_answer = msg.content
                    break

            if not final_answer and tool_output:
                final_answer = tool_output

            logger.info(f"[{user_id}/{project_id}/{session_id}] Completed. Tool: {tool_used}")

            return InvokeResponse(
                answer=final_answer,
                tool_used=tool_used,
                tool_output=tool_output
            )

        except Exception as e:
            logger.error(f"[{user_id}/{project_id}/{session_id}] Error: {e}")
            return InvokeResponse(error=str(e))

    async def close(self) -> None:
        """Clean up resources."""
        self._initialized = False
        logger.info("AgentOrchestrator closed - placeolder")
