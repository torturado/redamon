# RedAmon Agent Orchestrator

> **Iterative ReAct Agent for Autonomous Penetration Testing**

The RedAmon Agent Orchestrator is a LangGraph-based AI agent that performs penetration testing tasks using the **ReAct (Reasoning and Acting)** pattern. It combines iterative reasoning with tool execution, phase-based access control, and checkpoint-based user approval for dangerous operations.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Core Concepts](#core-concepts)
3. [Workflow Diagrams](#workflow-diagrams)
4. [Phase System](#phase-system)
5. [Tool System](#tool-system)
6. [State Management](#state-management)
7. [API Reference](#api-reference)
8. [Frontend Integration](#frontend-integration)
9. [Configuration](#configuration)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              REDAMON AGENT ARCHITECTURE                              │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│    ┌──────────────────┐     ┌──────────────────────────────────────────────────┐   │
│    │   Next.js App    │     │              Agent Orchestrator (Python)         │   │
│    │   (Frontend)     │     │                                                  │   │
│    │                  │     │   ┌────────────────────────────────────────────┐ │   │
│    │  ┌────────────┐  │     │   │           LangGraph StateGraph             │ │   │
│    │  │ AI Chat    │──┼────>│   │                                            │ │   │
│    │  │ Drawer     │  │     │   │  START → Initialize → Think ─────────────┐ │ │   │
│    │  └────────────┘  │     │   │                         │                 │ │ │   │
│    │        │         │     │   │                    ┌────┴────┐            │ │ │   │
│    │        │         │     │   │                    ▼         ▼            │ │ │   │
│    │  ┌────────────┐  │     │   │              Execute     Await           │ │ │   │
│    │  │ Phase      │  │     │   │               Tool      Approval ──┐     │ │ │   │
│    │  │ Indicator  │  │     │   │                 │          │       │     │ │ │   │
│    │  └────────────┘  │     │   │                 ▼          ▼       │     │ │ │   │
│    │        │         │     │   │              Analyze    Process    │     │ │ │   │
│    │  ┌────────────┐  │     │   │              Output    Approval   │     │ │ │   │
│    │  │ Approval   │  │     │   │                 │          │       │     │ │ │   │
│    │  │ Dialog     │<─┼─────┼───│                 └────┬─────┘       │     │ │ │   │
│    │  └────────────┘  │     │   │                      │             │     │ │ │   │
│    │                  │     │   │                      ▼             │     │ │ │   │
│    └──────────────────┘     │   │              Generate Response ────┴──>END│ │   │
│                             │   │                                            │ │   │
│                             │   └────────────────────────────────────────────┘ │   │
│                             │                          │                        │   │
│                             │                          ▼                        │   │
│                             │   ┌────────────────────────────────────────────┐ │   │
│                             │   │           Tool Executor Layer              │ │   │
│                             │   │                                            │ │   │
│                             │   │  ┌──────────┐ ┌──────────┐ ┌──────────┐   │ │   │
│                             │   │  │ Neo4j    │ │ MCP      │ │ MCP      │   │ │   │
│                             │   │  │ Graph    │ │ Curl     │ │ Naabu    │   │ │   │
│                             │   │  │ Query    │ │ Server   │ │ Server   │   │ │   │
│                             │   │  └────┬─────┘ └────┬─────┘ └────┬─────┘   │ │   │
│                             │   │       │            │            │         │ │   │
│                             │   │       │      ┌──────────┐       │         │ │   │
│                             │   │       │      │ MCP      │       │         │ │   │
│                             │   │       │      │Metasploit│       │         │ │   │
│                             │   │       │      │ Server   │       │         │ │   │
│                             │   │       │      └────┬─────┘       │         │ │   │
│                             │   └───────┼───────────┼─────────────┼─────────┘ │   │
│                             └───────────┼───────────┼─────────────┼───────────┘   │
│                                         │           │             │               │
│                                         ▼           ▼             ▼               │
│                             ┌───────────────────────────────────────────────────┐ │
│                             │                  External Services                 │ │
│                             │                                                   │ │
│                             │   ┌──────────┐   ┌──────────┐   ┌─────────────┐  │ │
│                             │   │  Neo4j   │   │   Kali   │   │  Metasploit │  │ │
│                             │   │ Database │   │ Sandbox  │   │   Console   │  │ │
│                             │   │          │   │(curl,    │   │             │  │ │
│                             │   │ (Graph   │   │ naabu)   │   │             │  │ │
│                             │   │  Data)   │   │          │   │             │  │ │
│                             │   └──────────┘   └──────────┘   └─────────────┘  │ │
│                             └───────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Core Concepts

### 1. ReAct Pattern (Reasoning and Acting)

The agent follows an iterative **Thought-Tool-Output** loop:

```
┌─────────────────────────────────────────────────────────────────┐
│                    ReAct Iteration Loop                         │
│                                                                 │
│    ┌──────────┐                                                │
│    │   USER   │                                                │
│    │  INPUT   │                                                │
│    └────┬─────┘                                                │
│         │                                                       │
│         ▼                                                       │
│    ┌──────────────────────────────────────────────────────┐    │
│    │                                                      │    │
│    │   ┌──────────┐      ┌──────────┐      ┌──────────┐  │    │
│    │   │  THINK   │ ──▶  │  ACTION  │ ──▶  │ OBSERVE  │  │    │
│    │   │          │      │          │      │          │  │    │
│    │   │ Analyze  │      │ Execute  │      │ Analyze  │  │    │
│    │   │ context  │      │ tool     │      │ output   │  │    │
│    │   │ Update   │      │          │      │ Extract  │  │    │
│    │   │ todos    │      │          │      │ intel    │  │    │
│    │   └──────────┘      └──────────┘      └────┬─────┘  │    │
│    │        ▲                                    │        │    │
│    │        │           ┌───────────┐            │        │    │
│    │        └───────────│  REFLECT  │◀───────────┘        │    │
│    │                    │           │                     │    │
│    │                    │ Continue? │                     │    │
│    │                    │ Complete? │                     │    │
│    │                    │ Transition│                     │    │
│    │                    │ phase?    │                     │    │
│    │                    └───────────┘                     │    │
│    │                                                      │    │
│    └──────────────────────────────────────────────────────┘    │
│         │                                                       │
│         ▼                                                       │
│    ┌──────────┐                                                │
│    │  FINAL   │                                                │
│    │  REPORT  │                                                │
│    └──────────┘                                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Key Principles:**

1. **Thought**: Before every action, the agent analyzes:
   - Current objective progress
   - Previous execution steps
   - Available target intelligence
   - Todo list status

2. **Action**: The agent selects and executes a tool:
   - `query_graph` - Query Neo4j database (PRIMARY source)
   - `execute_curl` - HTTP requests for verification
   - `execute_naabu` - Port scanning for verification
   - `metasploit_console` - Exploitation commands

3. **Observation**: After tool execution:
   - Parse and interpret output
   - Extract new intelligence
   - Update target information

4. **Reflection**: Decide next steps:
   - Continue with another tool?
   - Request phase transition?
   - Mark task as complete?

### 2. Graph-First Approach

The Neo4j database is the **PRIMARY source of truth** for all reconnaissance data:

```
┌─────────────────────────────────────────────────────────────────┐
│                  GRAPH-FIRST INFORMATION FLOW                   │
│                                                                 │
│   User Query: "What vulnerabilities exist on the target?"       │
│                              │                                  │
│                              ▼                                  │
│   ┌──────────────────────────────────────────────────────────┐ │
│   │                  STEP 1: QUERY GRAPH FIRST               │ │
│   │                                                          │ │
│   │   query_graph("Show all vulnerabilities for this project")│ │
│   │                         │                                 │ │
│   │                         ▼                                 │ │
│   │   ┌─────────────────────────────────────────────────────┐│ │
│   │   │                   NEO4J DATABASE                    ││ │
│   │   │                                                     ││ │
│   │   │   (Domain)──[:HAS]──>(Subdomain)──[:HAS]──>(IP)    ││ │
│   │   │        │                                     │      ││ │
│   │   │        └──────────────┬──────────────────────┘      ││ │
│   │   │                       ▼                             ││ │
│   │   │                    (Port)──[:HAS]──>(Service)       ││ │
│   │   │                       │                             ││ │
│   │   │                       ▼                             ││ │
│   │   │   (Vulnerability)◀──[:VULN]──(Technology)           ││ │
│   │   │        │                                            ││ │
│   │   │        ▼                                            ││ │
│   │   │      (CVE)                                          ││ │
│   │   │                                                     ││ │
│   │   └─────────────────────────────────────────────────────┘│ │
│   │                                                          │ │
│   └──────────────────────────────────────────────────────────┘ │
│                              │                                  │
│                              ▼                                  │
│   ┌──────────────────────────────────────────────────────────┐ │
│   │         STEP 2: VERIFY WITH AUXILIARY TOOLS              │ │
│   │         (Only if needed to confirm data)                 │ │
│   │                                                          │ │
│   │   execute_curl("-s -I http://target/vulnerable-endpoint")│ │
│   │                                                          │ │
│   │   execute_naabu("-host target -p 80,443 -json")         │ │
│   │                                                          │ │
│   └──────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Rules:**
- ALWAYS query Neo4j FIRST for any information need
- Use curl/naabu ONLY to VERIFY or UPDATE existing data
- NEVER run redundant scans for data already in the graph
- Trust graph data as the source of truth

### 3. LLM-Managed Todo List

The agent maintains a dynamic task list, updated at each iteration:

```
┌─────────────────────────────────────────────────────────────────┐
│                     TODO LIST MANAGEMENT                        │
│                                                                 │
│   Initial User Request:                                         │
│   "Find and exploit vulnerabilities on 10.0.0.5"                │
│                                                                 │
│   ┌───────────────────────────────────────────────────────────┐ │
│   │                    LLM CREATES TASKS                      │ │
│   │                                                           │ │
│   │   1. [~] !!! Query graph for target info          HIGH    │ │
│   │   2. [ ] !!  Identify open ports                  MEDIUM  │ │
│   │   3. [ ] !!  Check for known vulnerabilities      MEDIUM  │ │
│   │   4. [ ] !!! Verify exploitability               HIGH    │ │
│   │   5. [ ] !!  Prepare exploitation strategy        MEDIUM  │ │
│   │                                                           │ │
│   └───────────────────────────────────────────────────────────┘ │
│                              │                                  │
│                              ▼                                  │
│   ┌───────────────────────────────────────────────────────────┐ │
│   │              AFTER ITERATION 1 (Query Graph)              │ │
│   │                                                           │ │
│   │   1. [x] !!! Query graph for target info          HIGH    │ │
│   │   2. [~] !!  Identify open ports (ports found!)   MEDIUM  │ │
│   │   3. [ ] !!  Check for known vulnerabilities      MEDIUM  │ │
│   │   4. [ ] !!! Verify exploitability               HIGH    │ │
│   │   5. [ ] !!  Prepare exploitation strategy        MEDIUM  │ │
│   │   6. [ ] !!! CVE-2021-41773 detected - priority! HIGH    │ │
│   │                                                           │ │
│   └───────────────────────────────────────────────────────────┘ │
│                              │                                  │
│                              ▼                                  │
│   ┌───────────────────────────────────────────────────────────┐ │
│   │                 STATUS MEANINGS                           │ │
│   │                                                           │ │
│   │   [ ] pending      - Not started yet                      │ │
│   │   [~] in_progress  - Currently working on                 │ │
│   │   [x] completed    - Done                                 │ │
│   │   [!] blocked      - Cannot proceed (dependency/issue)    │ │
│   │                                                           │ │
│   │   !!! = HIGH priority                                     │ │
│   │   !!  = MEDIUM priority                                   │ │
│   │   !   = LOW priority                                      │ │
│   │                                                           │ │
│   └───────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Workflow Diagrams

### Complete Agent Flow

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              COMPLETE AGENT WORKFLOW                                │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│   ┌──────────┐                                                                     │
│   │  START   │                                                                     │
│   └────┬─────┘                                                                     │
│        │                                                                           │
│        ▼                                                                           │
│   ┌───────────────────┐                                                            │
│   │   INITIALIZE      │   - Set iteration = 0                                      │
│   │                   │   - Set phase = "informational"                            │
│   │                   │   - Parse objective from user message                      │
│   │                   │   - Initialize empty todo list                             │
│   └────────┬──────────┘                                                            │
│            │                                                                       │
│            ▼                                                                       │
│   ┌─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┐ │
│   │                        REACT ITERATION LOOP                                  │ │
│   │                                                                              │ │
│   │   ┌───────────────────┐                                                      │ │
│   │   │      THINK        │                                                      │ │
│   │   │                   │   Analyzes:                                          │ │
│   │   │   LLM Reasoning   │   - Current phase & restrictions                     │ │
│   │   │                   │   - Previous execution trace                         │ │
│   │   │                   │   - Todo list status                                 │ │
│   │   │                   │   - Target intelligence                              │ │
│   │   └────────┬──────────┘                                                      │ │
│   │            │                                                                  │ │
│   │            │  Outputs JSON decision:                                          │ │
│   │            │  {                                                               │ │
│   │            │    "thought": "...",                                             │ │
│   │            │    "action": "use_tool|transition_phase|complete",               │ │
│   │            │    "tool_name": "...",                                           │ │
│   │            │    "tool_args": {...},                                           │ │
│   │            │    "updated_todo_list": [...]                                    │ │
│   │            │  }                                                               │ │
│   │            │                                                                  │ │
│   │            ▼                                                                  │ │
│   │   ┌─────────────────────────────────────────────────────────────────┐        │ │
│   │   │                    ROUTING DECISION                             │        │ │
│   │   └────────────────────────────┬────────────────────────────────────┘        │ │
│   │                                │                                              │ │
│   │           ┌────────────────────┼────────────────────┐                        │ │
│   │           │                    │                    │                        │ │
│   │           ▼                    ▼                    ▼                        │ │
│   │   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │ │
│   │   │ action =     │    │ action =     │    │ action =     │                  │ │
│   │   │ "use_tool"   │    │ "transition" │    │ "complete"   │                  │ │
│   │   └──────┬───────┘    └──────┬───────┘    └──────┬───────┘                  │ │
│   │          │                   │                   │                           │ │
│   │          ▼                   ▼                   │                           │ │
│   │   ┌──────────────┐    ┌──────────────┐          │                           │ │
│   │   │EXECUTE TOOL  │    │AWAIT APPROVAL│          │                           │ │
│   │   │              │    │              │          │                           │ │
│   │   │- Check phase │    │- Pause graph │          │                           │ │
│   │   │  restriction │    │- Wait for    │          │                           │ │
│   │   │- Invoke tool │    │  user input  │          │                           │ │
│   │   │- Capture     │    │              │          │                           │ │
│   │   │  output      │    └──────┬───────┘          │                           │ │
│   │   └──────┬───────┘           │                  │                           │ │
│   │          │                   │                  │                           │ │
│   │          ▼                   │  ────> END       │                           │ │
│   │   ┌──────────────┐           │  (Graph Paused)  │                           │ │
│   │   │ANALYZE OUTPUT│           │                  │                           │ │
│   │   │              │           │                  │                           │ │
│   │   │- LLM parses  │    ┌──────────────┐         │                           │ │
│   │   │  result      │    │   /approve   │         │                           │ │
│   │   │- Extract     │    │   endpoint   │         │                           │ │
│   │   │  intel       │    │   called     │         │                           │ │
│   │   │- Update      │    └──────┬───────┘         │                           │ │
│   │   │  target_info │           │                  │                           │ │
│   │   │- Add to      │           ▼                  │                           │ │
│   │   │  trace       │    ┌──────────────┐         │                           │ │
│   │   └──────┬───────┘    │   PROCESS    │         │                           │ │
│   │          │            │   APPROVAL   │         │                           │ │
│   │          │            │              │         │                           │ │
│   │          │            │ approve -->  │         │                           │ │
│   │          │            │  transition  │         │                           │ │
│   │          │            │  to new phase│         │                           │ │
│   │          │            │              │         │                           │ │
│   │          │            │ modify -->   │         │                           │ │
│   │          │            │  stay in     │         │                           │ │
│   │          │            │  current     │         │                           │ │
│   │          │            │  phase       │         │                           │ │
│   │          │            │              │         │                           │ │
│   │          │            │ abort -->    │─────────┼─────────┐                  │ │
│   │          │            │  end session │         │         │                  │ │
│   │          │            └──────┬───────┘         │         │                  │ │
│   │          │                   │                 │         │                  │ │
│   │          └───────────────────┼─────────────────┘         │                  │ │
│   │                              │                            │                  │ │
│   │                              ▼                            │                  │ │
│   │                      ┌──────────────────┐                │                  │ │
│   │                      │ Max iterations?  │                │                  │ │
│   │                      │ Task complete?   │                │                  │ │
│   │                      └────────┬─────────┘                │                  │ │
│   │                               │                          │                  │ │
│   │                    ┌──────────┴──────────┐               │                  │ │
│   │                    │                     │               │                  │ │
│   │                    ▼                     ▼               │                  │ │
│   │                Continue              Complete            │                  │ │
│   │                (loop back             (exit loop)        │                  │ │
│   │                to THINK)                 │               │                  │ │
│   │                    │                     │               │                  │ │
│   └ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─│─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─│─ ─ ─ ─ ─ ─ ─ ─│─ ─ ─ ─ ─ ─ ─ ─ ─┘ │
│                        │                     │               │                   │
│                        │                     ▼               ▼                   │
│                        │            ┌───────────────────────────┐               │
│                        │            │    GENERATE RESPONSE      │               │
│                        │            │                           │               │
│                        │            │  - Summarize session      │               │
│                        │            │  - Key findings           │               │
│                        │            │  - Vulnerabilities        │               │
│                        │            │  - Recommendations        │               │
│                        │            └─────────────┬─────────────┘               │
│                        │                          │                              │
│                        │                          ▼                              │
│                        │                    ┌──────────┐                        │
│                        │                    │   END    │                        │
│                        │                    └──────────┘                        │
│                        │                                                         │
│                        └──────────────────> (back to THINK)                      │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### Approval Flow Detail

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           PHASE TRANSITION APPROVAL FLOW                            │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│   Agent wants to transition from INFORMATIONAL to EXPLOITATION                      │
│                                                                                     │
│   ┌───────────────────────────────────────────────────────────────────────────┐    │
│   │                         1. AGENT CREATES REQUEST                          │    │
│   │                                                                           │    │
│   │   {                                                                       │    │
│   │     "from_phase": "informational",                                        │    │
│   │     "to_phase": "exploitation",                                           │    │
│   │     "reason": "Found CVE-2021-41773 on Apache 2.4.49, ready to exploit", │    │
│   │     "planned_actions": [                                                  │    │
│   │       "Use Metasploit's apache_normalize_path_rce module",               │    │
│   │       "Set RHOSTS to 10.0.0.5",                                          │    │
│   │       "Attempt exploitation with reverse shell payload"                   │    │
│   │     ],                                                                    │    │
│   │     "risks": [                                                            │    │
│   │       "Service disruption possible",                                      │    │
│   │       "May trigger IDS/IPS alerts",                                       │    │
│   │       "Target system could crash"                                         │    │
│   │     ]                                                                     │    │
│   │   }                                                                       │    │
│   │                                                                           │    │
│   └───────────────────────────────────────────────────────────────────────────┘    │
│                                        │                                            │
│                                        ▼                                            │
│   ┌───────────────────────────────────────────────────────────────────────────┐    │
│   │                     2. GRAPH EXECUTION PAUSES                             │    │
│   │                                                                           │    │
│   │   - State saved to MemorySaver checkpointer                               │    │
│   │   - awaiting_user_approval = true                                         │    │
│   │   - phase_transition_pending = <request above>                            │    │
│   │   - API returns to frontend with approval request                         │    │
│   │                                                                           │    │
│   └───────────────────────────────────────────────────────────────────────────┘    │
│                                        │                                            │
│                                        ▼                                            │
│   ┌───────────────────────────────────────────────────────────────────────────┐    │
│   │                     3. FRONTEND SHOWS DIALOG                              │    │
│   │                                                                           │    │
│   │   ┌─────────────────────────────────────────────────────────────────┐    │    │
│   │   │  Phase Transition Request                                        │    │    │
│   │   │                                                                  │    │    │
│   │   │  ┌─────────────┐    -->    ┌─────────────────┐                 │    │    │
│   │   │  │INFORMATIONAL│           │  EXPLOITATION   │                 │    │    │
│   │   │  └─────────────┘           └─────────────────┘                 │    │    │
│   │   │                                                                  │    │    │
│   │   │  Reason:                                                         │    │    │
│   │   │  Found CVE-2021-41773 on Apache 2.4.49, ready to exploit        │    │    │
│   │   │                                                                  │    │    │
│   │   │  Planned Actions:                                                │    │    │
│   │   │  - Use Metasploit's apache_normalize_path_rce module            │    │    │
│   │   │  - Set RHOSTS to 10.0.0.5                                       │    │    │
│   │   │  - Attempt exploitation with reverse shell payload              │    │    │
│   │   │                                                                  │    │    │
│   │   │  Risks:                                                          │    │    │
│   │   │  - Service disruption possible                                   │    │    │
│   │   │  - May trigger IDS/IPS alerts                                   │    │    │
│   │   │                                                                  │    │    │
│   │   │  ┌───────────┐  ┌───────────┐  ┌───────────┐                   │    │    │
│   │   │  │  APPROVE  │  │  MODIFY   │  │   ABORT   │                   │    │    │
│   │   │  └───────────┘  └───────────┘  └───────────┘                   │    │    │
│   │   │                                                                  │    │    │
│   │   └─────────────────────────────────────────────────────────────────┘    │    │
│   │                                                                           │    │
│   └───────────────────────────────────────────────────────────────────────────┘    │
│                                        │                                            │
│              ┌─────────────────────────┼─────────────────────────┐                 │
│              │                         │                         │                 │
│              ▼                         ▼                         ▼                 │
│      ┌──────────────┐         ┌──────────────┐         ┌──────────────┐           │
│      │   APPROVE    │         │    MODIFY    │         │    ABORT     │           │
│      └──────┬───────┘         └──────┬───────┘         └──────┬───────┘           │
│             │                        │                        │                    │
│             ▼                        ▼                        ▼                    │
│   ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐             │
│   │ Transition to   │     │ Stay in current │     │ End session     │             │
│   │ EXPLOITATION    │     │ phase           │     │ Generate report │             │
│   │ phase           │     │                 │     │                 │             │
│   │                 │     │ Add user's      │     │                 │             │
│   │ Continue with   │     │ modification to │     │                 │             │
│   │ planned actions │     │ context         │     │                 │             │
│   │                 │     │                 │     │                 │             │
│   │ metasploit      │     │ Continue with   │     │                 │             │
│   │ tools unlocked  │     │ adjusted plan   │     │                 │             │
│   └─────────────────┘     └─────────────────┘     └─────────────────┘             │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Phase System

### Phase Definitions

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              PHASE DEFINITIONS                                      │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│   ┌─────────────────────────────────────────────────────────────────────────────┐  │
│   │                        INFORMATIONAL (Default)                              │  │
│   │                                                                             │  │
│   │   Purpose:                                                                  │  │
│   │   - Gather intelligence about the target                                    │  │
│   │   - Query existing reconnaissance data                                      │  │
│   │   - Verify and update information                                           │  │
│   │                                                                             │  │
│   │   Allowed Tools:                                                            │  │
│   │   |-- query_graph     (PRIMARY - always use first)                         │  │
│   │   |-- execute_curl    (HTTP verification)                                   │  │
│   │   +-- execute_naabu   (Port verification)                                   │  │
│   │                                                                             │  │
│   │   Entry Condition: Default starting phase                                   │  │
│   │   Exit: Request transition to exploitation                                  │  │
│   │                                                                             │  │
│   └─────────────────────────────────────────────────────────────────────────────┘  │
│                                        │                                            │
│                            ┌───────────┴───────────┐                               │
│                            │   User Approval       │                               │
│                            │   Required            │                               │
│                            └───────────┬───────────┘                               │
│                                        ▼                                            │
│   ┌─────────────────────────────────────────────────────────────────────────────┐  │
│   │                           EXPLOITATION                                      │  │
│   │                                                                             │  │
│   │   Purpose:                                                                  │  │
│   │   - Actively exploit confirmed vulnerabilities                              │  │
│   │   - Gain initial access to target systems                                   │  │
│   │   - Execute payloads and obtain sessions                                    │  │
│   │                                                                             │  │
│   │   Allowed Tools:                                                            │  │
│   │   |-- query_graph                                                           │  │
│   │   |-- execute_curl                                                          │  │
│   │   |-- execute_naabu                                                         │  │
│   │   +-- metasploit_console  (NEW - exploitation capabilities)                │  │
│   │       |-- search exploits                                                   │  │
│   │       |-- configure modules                                                 │  │
│   │       |-- run exploits                                                      │  │
│   │       +-- manage handlers                                                   │  │
│   │                                                                             │  │
│   │   Entry Condition: Confirmed vulnerability + user approval                  │  │
│   │   Exit: Request transition to post_exploitation (after getting session)    │  │
│   │                                                                             │  │
│   └─────────────────────────────────────────────────────────────────────────────┘  │
│                                        │                                            │
│                            ┌───────────┴───────────┐                               │
│                            │   User Approval       │                               │
│                            │   Required            │                               │
│                            └───────────┬───────────┘                               │
│                                        ▼                                            │
│   ┌─────────────────────────────────────────────────────────────────────────────┐  │
│   │                        POST-EXPLOITATION                                    │  │
│   │                                                                             │  │
│   │   Purpose:                                                                  │  │
│   │   - Interact with compromised systems                                       │  │
│   │   - Enumerate system information                                            │  │
│   │   - Gather credentials                                                      │  │
│   │   - Establish persistence                                                   │  │
│   │   - Prepare for lateral movement                                            │  │
│   │                                                                             │  │
│   │   Allowed Tools:                                                            │  │
│   │   |-- All exploitation tools                                                │  │
│   │   +-- metasploit_console (Extended)                                         │  │
│   │       |-- sessions -l / sessions -i                                         │  │
│   │       |-- meterpreter commands                                              │  │
│   │       │   |-- sysinfo, getuid                                               │  │
│   │       │   |-- hashdump                                                      │  │
│   │       │   |-- shell                                                         │  │
│   │       │   +-- persistence modules                                           │  │
│   │       +-- post-exploitation modules                                         │  │
│   │                                                                             │  │
│   │   Entry Condition: Active session + user approval                           │  │
│   │                                                                             │  │
│   └─────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### Phase Transition Flow

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           PHASE TRANSITION MATRIX                                   │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│                    TO                                                               │
│                    │                                                                │
│       ┌────────────┼────────────────┬──────────────────┬──────────────────┐        │
│       │            │ INFORMATIONAL  │  EXPLOITATION    │ POST-EXPLOITATION│        │
│  FROM ├────────────┼────────────────┼──────────────────┼──────────────────┤        │
│       │INFORMATIONAL│     N/A       │  Y (approval)    │  X (not direct)  │        │
│       ├────────────┼────────────────┼──────────────────┼──────────────────┤        │
│       │EXPLOITATION │  Y (always)   │       N/A        │  Y (approval)    │        │
│       ├────────────┼────────────────┼──────────────────┼──────────────────┤        │
│       │POST-EXPLOIT │  Y (always)   │   Y (always)     │       N/A        │        │
│       └────────────┴────────────────┴──────────────────┴──────────────────┘        │
│                                                                                     │
│   Legend:                                                                           │
│   Y (approval) = Requires user approval                                            │
│   Y (always)   = Can transition without approval (going back)                      │
│   X            = Not allowed / Must go through intermediate phase                  │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Tool System

### Tool Phase Restrictions

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                            TOOL PHASE RESTRICTIONS                                  │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│   Tool Name           │ INFORMATIONAL │ EXPLOITATION │ POST-EXPLOITATION           │
│   ────────────────────┼───────────────┼──────────────┼─────────────────            │
│   query_graph         │      Y        │      Y       │       Y                     │
│   execute_curl        │      Y        │      Y       │       Y                     │
│   execute_naabu       │      Y        │      Y       │       Y                     │
│   metasploit_console  │      X        │      Y       │       Y                     │
│                                                                                     │
│   ────────────────────────────────────────────────────────────────────────────────  │
│                                                                                     │
│   If agent tries to use a restricted tool:                                          │
│                                                                                     │
│   ┌───────────────────────────────────────────────────────────────────────────┐    │
│   │ Agent in INFORMATIONAL phase tries: metasploit_console("search CVE...")   │    │
│   │                                                                           │    │
│   │ Result:                                                                   │    │
│   │ {                                                                         │    │
│   │   "success": false,                                                       │    │
│   │   "error": "Tool 'metasploit_console' is not allowed in 'informational'  │    │
│   │             phase. This tool requires: exploitation"                      │    │
│   │ }                                                                         │    │
│   │                                                                           │    │
│   │ Agent must request phase transition first!                                │    │
│   └───────────────────────────────────────────────────────────────────────────┘    │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### Tool Descriptions

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              AVAILABLE TOOLS                                        │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│   ┌─────────────────────────────────────────────────────────────────────────────┐  │
│   │  1. query_graph (PRIMARY)                                                   │  │
│   │                                                                             │  │
│   │  Query Neo4j database using natural language. This tool translates         │  │
│   │  questions to Cypher queries and automatically applies tenant filtering.    │  │
│   │                                                                             │  │
│   │  Arguments:                                                                 │  │
│   │  {                                                                          │  │
│   │    "question": "What vulnerabilities exist on 10.0.0.5?"                    │  │
│   │  }                                                                          │  │
│   │                                                                             │  │
│   │  Contains: Domains, Subdomains, IPs, Ports, Services, Technologies,        │  │
│   │            Vulnerabilities, CVEs, MITRE ATT&CK mappings                     │  │
│   │                                                                             │  │
│   │  Example queries:                                                           │  │
│   │  - "Show all critical vulnerabilities for this project"                    │  │
│   │  - "What ports are open on the target?"                                    │  │
│   │  - "What technologies are running on port 443?"                            │  │
│   │  - "List all CVEs with CVSS > 7"                                           │  │
│   │                                                                             │  │
│   └─────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                     │
│   ┌─────────────────────────────────────────────────────────────────────────────┐  │
│   │  2. execute_curl (Auxiliary)                                                │  │
│   │                                                                             │  │
│   │  Make HTTP requests to verify endpoints or test specific URLs.              │  │
│   │  Use ONLY to verify information from the graph.                             │  │
│   │                                                                             │  │
│   │  Arguments:                                                                 │  │
│   │  {                                                                          │  │
│   │    "args": "-s -I http://target.com"                                        │  │
│   │  }                                                                          │  │
│   │                                                                             │  │
│   │  Example uses:                                                              │  │
│   │  - "-s -I http://target.com"           (get headers)                       │  │
│   │  - "-s http://target/api/health"       (check endpoint)                    │  │
│   │  - "-s -X POST -d '{}' http://..."     (test POST)                         │  │
│   │                                                                             │  │
│   └─────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                     │
│   ┌─────────────────────────────────────────────────────────────────────────────┐  │
│   │  3. execute_naabu (Auxiliary)                                               │  │
│   │                                                                             │  │
│   │  Fast port scanner for verification. Use to verify ports are open          │  │
│   │  or scan new targets not already in the graph.                              │  │
│   │                                                                             │  │
│   │  Arguments:                                                                 │  │
│   │  {                                                                          │  │
│   │    "args": "-host 10.0.0.5 -p 80,443,8080 -json"                            │  │
│   │  }                                                                          │  │
│   │                                                                             │  │
│   │  Example uses:                                                              │  │
│   │  - "-host 10.0.0.5 -p 80,443"          (verify specific ports)             │  │
│   │  - "-host 10.0.0.5 -top-ports 100"     (scan top ports)                    │  │
│   │  - "-host 10.0.0.0/24 -p 22 -json"     (scan subnet for SSH)               │  │
│   │                                                                             │  │
│   └─────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                     │
│   ┌─────────────────────────────────────────────────────────────────────────────┐  │
│   │  4. metasploit_console (Exploitation/Post-Exploitation Only)                │  │
│   │                                                                             │  │
│   │  Execute commands in a persistent Metasploit console.                       │  │
│   │  Console maintains state between calls (sessions, handlers persist).        │  │
│   │                                                                             │  │
│   │  Arguments:                                                                 │  │
│   │  {                                                                          │  │
│   │    "command": "search type:exploit CVE-2021-41773"                          │  │
│   │  }                                                                          │  │
│   │                                                                             │  │
│   │  Common commands:                                                           │  │
│   │                                                                             │  │
│   │  EXPLOITATION PHASE:                                                        │  │
│   │  - "search CVE-2021-41773"                     (find exploits)             │  │
│   │  - "use exploit/multi/http/apache_normalize_path_rce"  (select module)     │  │
│   │  - "info"                                      (get module info)           │  │
│   │  - "show options"                              (view options)              │  │
│   │  - "set RHOSTS 10.0.0.5"                       (set target)                │  │
│   │  - "set PAYLOAD linux/x64/meterpreter/reverse_tcp"  (set payload)          │  │
│   │  - "check"                                     (verify vulnerable)          │  │
│   │  - "exploit -j"                                (run in background)         │  │
│   │                                                                             │  │
│   │  POST-EXPLOITATION PHASE:                                                   │  │
│   │  - "sessions -l"                               (list sessions)             │  │
│   │  - "sessions -i 1"                             (interact with session)     │  │
│   │  - "sysinfo"                                   (system information)        │  │
│   │  - "getuid"                                    (current user)              │  │
│   │  - "hashdump"                                  (dump hashes)               │  │
│   │  - "shell"                                     (get system shell)          │  │
│   │  - "background"                                (return to msfconsole)      │  │
│   │                                                                             │  │
│   └─────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## State Management

### AgentState Structure

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              AGENTSTATE (TypedDict)                                 │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│   ┌─────────────────────────────────────────────────────────────────────────────┐  │
│   │  CORE CONVERSATION                                                          │  │
│   │  -----------------                                                          │  │
│   │  messages: List[Message]           # Managed by add_messages reducer        │  │
│   │                                     # Contains all Human/AI messages         │  │
│   └─────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                     │
│   ┌─────────────────────────────────────────────────────────────────────────────┐  │
│   │  REACT LOOP CONTROL                                                         │  │
│   │  ------------------                                                         │  │
│   │  current_iteration: int            # Current step number (1, 2, 3...)       │  │
│   │  max_iterations: int               # Limit before forced stop (default: 15) │  │
│   │  task_complete: bool               # True when objective achieved           │  │
│   │  completion_reason: str | None     # Why the task ended                     │  │
│   └─────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                     │
│   ┌─────────────────────────────────────────────────────────────────────────────┐  │
│   │  PHASE TRACKING                                                             │  │
│   │  --------------                                                             │  │
│   │  current_phase: "informational" | "exploitation" | "post_exploitation"      │  │
│   │  phase_history: List[{                                                      │  │
│   │      "phase": str,                                                          │  │
│   │      "entered_at": datetime,                                                │  │
│   │      "exited_at": datetime | None                                           │  │
│   │  }]                                                                         │  │
│   │  phase_transition_pending: {       # When awaiting approval                 │  │
│   │      "from_phase": str,                                                     │  │
│   │      "to_phase": str,                                                       │  │
│   │      "reason": str,                                                         │  │
│   │      "planned_actions": List[str],                                          │  │
│   │      "risks": List[str]                                                     │  │
│   │  } | None                                                                   │  │
│   └─────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                     │
│   ┌─────────────────────────────────────────────────────────────────────────────┐  │
│   │  EXECUTION TRACE                                                            │  │
│   │  ---------------                                                            │  │
│   │  execution_trace: List[{                                                    │  │
│   │      "step_id": str,               # Unique ID (8 chars)                    │  │
│   │      "iteration": int,             # Which iteration                        │  │
│   │      "timestamp": datetime,        # When executed                          │  │
│   │      "phase": str,                 # Phase during execution                 │  │
│   │      "thought": str,               # Agent's reasoning                      │  │
│   │      "reasoning": str,             # Why this action was chosen             │  │
│   │      "tool_name": str | None,      # Tool used (if any)                     │  │
│   │      "tool_args": dict | None,     # Arguments passed                       │  │
│   │      "tool_output": str | None,    # Raw output                             │  │
│   │      "output_analysis": str | None,# Agent's interpretation                 │  │
│   │      "success": bool,              # Did it work?                           │  │
│   │      "error_message": str | None   # Error if failed                        │  │
│   │  }]                                                                         │  │
│   └─────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                     │
│   ┌─────────────────────────────────────────────────────────────────────────────┐  │
│   │  TODO LIST                                                                  │  │
│   │  ---------                                                                  │  │
│   │  todo_list: List[{                                                          │  │
│   │      "id": str,                    # Unique ID (8 chars)                    │  │
│   │      "description": str,           # Task description                       │  │
│   │      "status": "pending" | "in_progress" | "completed" | "blocked",         │  │
│   │      "priority": "high" | "medium" | "low",                                 │  │
│   │      "notes": str | None,          # Additional context                     │  │
│   │      "created_at": datetime,                                                │  │
│   │      "completed_at": datetime | None                                        │  │
│   │  }]                                                                         │  │
│   │  original_objective: str           # The initial user request               │  │
│   └─────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                     │
│   ┌─────────────────────────────────────────────────────────────────────────────┐  │
│   │  TARGET INTELLIGENCE                                                        │  │
│   │  --------------------                                                       │  │
│   │  target_info: {                                                             │  │
│   │      "primary_target": str | None,  # Main target (IP/hostname)            │  │
│   │      "target_type": "ip" | "hostname" | "domain" | "url" | None,           │  │
│   │      "ports": List[int],            # Discovered ports                      │  │
│   │      "services": List[str],         # Running services                      │  │
│   │      "technologies": List[str],     # Detected tech stack                   │  │
│   │      "vulnerabilities": List[str],  # Found vulns/CVEs                      │  │
│   │      "credentials": List[dict],     # Discovered credentials                │  │
│   │      "sessions": List[int]          # Active Metasploit sessions            │  │
│   │  }                                                                          │  │
│   └─────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                     │
│   ┌─────────────────────────────────────────────────────────────────────────────┐  │
│   │  SESSION CONTEXT                                                            │  │
│   │  ---------------                                                            │  │
│   │  user_id: str                      # Current user ID                        │  │
│   │  project_id: str                   # Current project ID                     │  │
│   │  session_id: str                   # Session for continuity                 │  │
│   └─────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                     │
│   ┌─────────────────────────────────────────────────────────────────────────────┐  │
│   │  APPROVAL CONTROL                                                           │  │
│   │  ----------------                                                           │  │
│   │  awaiting_user_approval: bool      # True when paused for approval          │  │
│   │  user_approval_response: "approve" | "modify" | "abort" | None              │  │
│   │  user_modification: str | None     # User's changes if "modify"             │  │
│   └─────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### State Persistence

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              STATE PERSISTENCE                                      │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│   All agent state is stored in memory using LangGraph's MemorySaver checkpointer.  │
│   State is NOT persisted to Neo4j - Neo4j is only for reconnaissance data.         │
│                                                                                     │
│   ┌─────────────────────────────────────────────────────────────────────────────┐  │
│   │                        SESSION CONTINUITY                                   │  │
│   │                                                                             │  │
│   │   Request 1: "Find vulnerabilities on 10.0.0.5"                             │  │
│   │       │                                                                     │  │
│   │       ▼                                                                     │  │
│   │   ┌──────────────────┐     ┌──────────────────┐                            │  │
│   │   │   API Handler    │────>│  MemorySaver     │                            │  │
│   │   │                  │     │  checkpointer    │                            │  │
│   │   │ session_id =     │     │                  │                            │  │
│   │   │ "session-001"    │     │  Stores state    │                            │  │
│   │   └──────────────────┘     │  keyed by:       │                            │  │
│   │                            │  user_id +       │                            │  │
│   │   Request 2: (same session)│  project_id +    │                            │  │
│   │       │                    │  session_id      │                            │  │
│   │       ▼                    │                  │                            │  │
│   │   ┌──────────────────┐     │                  │                            │  │
│   │   │   API Handler    │────>│  Retrieves       │                            │  │
│   │   │                  │<────│  previous state  │                            │  │
│   │   │ session_id =     │     │                  │                            │  │
│   │   │ "session-001"    │     │  Continues       │                            │  │
│   │   └──────────────────┘     │  conversation    │                            │  │
│   │                            └──────────────────┘                            │  │
│   │                                                                             │  │
│   └─────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                     │
│   ┌─────────────────────────────────────────────────────────────────────────────┐  │
│   │                     APPROVAL PAUSE/RESUME                                   │  │
│   │                                                                             │  │
│   │   1. Agent wants phase transition                                           │  │
│   │       │                                                                     │  │
│   │       ▼                                                                     │  │
│   │   awaiting_user_approval = true                                             │  │
│   │   phase_transition_pending = {...}                                          │  │
│   │       │                                                                     │  │
│   │       ▼                                                                     │  │
│   │   Graph execution ENDS (state saved to checkpointer)                        │  │
│   │       │                                                                     │  │
│   │       ▼                                                                     │  │
│   │   API returns response with awaiting_approval: true                         │  │
│   │                                                                             │  │
│   │   -----------------------------------------------------------------         │  │
│   │                                                                             │  │
│   │   2. User clicks "Approve" in frontend                                      │  │
│   │       │                                                                     │  │
│   │       ▼                                                                     │  │
│   │   POST /approve                                                             │  │
│   │   {                                                                         │  │
│   │     "session_id": "session-001",                                            │  │
│   │     "decision": "approve"                                                   │  │
│   │   }                                                                         │  │
│   │       │                                                                     │  │
│   │       ▼                                                                     │  │
│   │   orchestrator.resume_after_approval(...)                                   │  │
│   │       │                                                                     │  │
│   │       ▼                                                                     │  │
│   │   State retrieved from checkpointer                                         │  │
│   │   Graph execution RESUMES from process_approval node                        │  │
│   │                                                                             │  │
│   └─────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## API Reference

### Endpoints

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                API ENDPOINTS                                        │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│   BASE URL: http://localhost:8080                                                   │
│                                                                                     │
│   ┌─────────────────────────────────────────────────────────────────────────────┐  │
│   │  POST /query                                                                │  │
│   │                                                                             │  │
│   │  Send a question to the ReAct agent.                                        │  │
│   │                                                                             │  │
│   │  Request:                                                                   │  │
│   │  {                                                                          │  │
│   │    "question": "Find vulnerabilities on 10.0.0.5",                          │  │
│   │    "user_id": "user1",                                                      │  │
│   │    "project_id": "project1",                                                │  │
│   │    "session_id": "session-001"                                              │  │
│   │  }                                                                          │  │
│   │                                                                             │  │
│   │  Response:                                                                  │  │
│   │  {                                                                          │  │
│   │    "answer": "I found CVE-2021-41773 on Apache 2.4.49...",                 │  │
│   │    "tool_used": "query_graph",                                              │  │
│   │    "tool_output": "[{...}]",                                                │  │
│   │    "session_id": "session-001",                                             │  │
│   │    "message_count": 3,                                                      │  │
│   │    "error": null,                                                           │  │
│   │    "current_phase": "informational",                                        │  │
│   │    "iteration_count": 2,                                                    │  │
│   │    "task_complete": false,                                                  │  │
│   │    "todo_list": [                                                           │  │
│   │      {"id": "abc123", "description": "...", "status": "completed", ...}    │  │
│   │    ],                                                                       │  │
│   │    "execution_trace_summary": [                                             │  │
│   │      {"iteration": 1, "phase": "informational", "thought": "...", ...}     │  │
│   │    ],                                                                       │  │
│   │    "awaiting_approval": false,                                              │  │
│   │    "approval_request": null                                                 │  │
│   │  }                                                                          │  │
│   │                                                                             │  │
│   └─────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                     │
│   ┌─────────────────────────────────────────────────────────────────────────────┐  │
│   │  POST /approve                                                              │  │
│   │                                                                             │  │
│   │  Respond to a phase transition approval request.                            │  │
│   │                                                                             │  │
│   │  Request:                                                                   │  │
│   │  {                                                                          │  │
│   │    "session_id": "session-001",                                             │  │
│   │    "user_id": "user1",                                                      │  │
│   │    "project_id": "project1",                                                │  │
│   │    "decision": "approve" | "modify" | "abort",                              │  │
│   │    "modification": "Focus on port 8080 instead"  // Only if modify          │  │
│   │  }                                                                          │  │
│   │                                                                             │  │
│   │  Response: Same format as /query                                            │  │
│   │                                                                             │  │
│   └─────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                     │
│   ┌─────────────────────────────────────────────────────────────────────────────┐  │
│   │  GET /health                                                                │  │
│   │                                                                             │  │
│   │  Health check endpoint.                                                     │  │
│   │                                                                             │  │
│   │  Response:                                                                  │  │
│   │  {                                                                          │  │
│   │    "status": "ok",                                                          │  │
│   │    "version": "2.0.0",                                                      │  │
│   │    "tools_loaded": 4,                                                       │  │
│   │    "active_sessions": 2                                                     │  │
│   │  }                                                                          │  │
│   │                                                                             │  │
│   └─────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Frontend Integration

### AI Assistant Drawer

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                          FRONTEND INTEGRATION                                       │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│   The webapp includes an AI Assistant drawer that displays:                         │
│                                                                                     │
│   ┌───────────────────────────────────────────────────────┐                        │
│   │  ┌─────────────────────────────────────────────────┐  │                        │
│   │  │  RedAmon AI                                  X  │  │  <- Header             │
│   │  │     Penetration Testing Assistant               │  │                        │
│   │  └─────────────────────────────────────────────────┘  │                        │
│   │  ┌─────────────────────────────────────────────────┐  │                        │
│   │  │  INFORMATIONAL                    Step 3/15     │  │  <- Phase Indicator    │
│   │  └─────────────────────────────────────────────────┘  │                        │
│   │  ┌─────────────────────────────────────────────────┐  │                        │
│   │  │                                                 │  │                        │
│   │  │  [User] Find vulnerabilities on 10.0.0.5       │  │  <- User Message       │
│   │  │                                                 │  │                        │
│   │  │  [AI] I found CVE-2021-41773 on Apache 2.4.49  │  │  <- AI Response        │
│   │  │     running on port 443.                        │  │                        │
│   │  │                                                 │  │                        │
│   │  │     [Tool] query_graph                         │  │  <- Tool Badge         │
│   │  │     ┌──────────────────────────────────────┐   │  │                        │
│   │  │     │ [{"CVE": "CVE-2021-41773", ...}]     │   │  │  <- Tool Output        │
│   │  │     └──────────────────────────────────────┘   │  │                        │
│   │  │                                                 │  │                        │
│   │  └─────────────────────────────────────────────────┘  │                        │
│   │  ┌─────────────────────────────────────────────────┐  │                        │
│   │  │  Type your message...                    [>]   │  │  <- Input Area         │
│   │  └─────────────────────────────────────────────────┘  │                        │
│   └───────────────────────────────────────────────────────┘                        │
│                                                                                     │
│   WHEN APPROVAL IS REQUIRED:                                                        │
│                                                                                     │
│   ┌───────────────────────────────────────────────────┐                            │
│   │  ┌─────────────────────────────────────────────┐  │                            │
│   │  │  [!] Phase Transition Request               │  │                            │
│   │  │                                             │  │                            │
│   │  │  ┌───────────────┐   >   ┌──────────────┐  │  │                            │
│   │  │  │ INFORMATIONAL │       │ EXPLOITATION │  │  │                            │
│   │  │  └───────────────┘       └──────────────┘  │  │                            │
│   │  │                                             │  │                            │
│   │  │  Reason:                                    │  │                            │
│   │  │  Found CVE-2021-41773, ready to exploit    │  │                            │
│   │  │                                             │  │                            │
│   │  │  Planned Actions:                           │  │                            │
│   │  │  - Use apache_normalize_path_rce module    │  │                            │
│   │  │  - Set RHOSTS to 10.0.0.5                  │  │                            │
│   │  │                                             │  │                            │
│   │  │  Risks:                                     │  │                            │
│   │  │  - Service disruption possible              │  │                            │
│   │  │                                             │  │                            │
│   │  │  ┌───────────┐ ┌────────┐ ┌───────────┐   │  │                            │
│   │  │  │  APPROVE  │ │ MODIFY │ │   ABORT   │   │  │                            │
│   │  │  └───────────┘ └────────┘ └───────────┘   │  │                            │
│   │  │                                             │  │                            │
│   │  └─────────────────────────────────────────────┘  │                            │
│   └───────────────────────────────────────────────────┘                            │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Configuration

### Environment Variables

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                          CONFIGURATION (params.py)                                  │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│   LLM CONFIGURATION                                                                 │
│   -----------------                                                                 │
│   OPENAI_MODEL = "gpt-4.1"              # LLM model to use                         │
│   OPENAI_API_KEY = <from env>           # API key                                   │
│                                                                                     │
│   MCP SERVER URLs                                                                   │
│   ---------------                                                                   │
│   MCP_CURL_URL = "http://host.docker.internal:8001/sse"                            │
│   MCP_NAABU_URL = "http://host.docker.internal:8000/sse"                           │
│   MCP_METASPLOIT_URL = "http://host.docker.internal:8003/sse"                      │
│                                                                                     │
│   REACT AGENT SETTINGS                                                              │
│   --------------------                                                              │
│   MAX_ITERATIONS = 15                   # Stop after N iterations                   │
│   REQUIRE_APPROVAL_FOR_EXPLOITATION = true      # Pause before exploitation        │
│   REQUIRE_APPROVAL_FOR_POST_EXPLOITATION = true # Pause before post-exploitation   │
│                                                                                     │
│   NEO4J SETTINGS                                                                    │
│   --------------                                                                    │
│   NEO4J_URI = "bolt://localhost:7687"                                              │
│   NEO4J_USER = "neo4j"                                                             │
│   NEO4J_PASSWORD = <from env>                                                      │
│   CYPHER_MAX_RETRIES = 3                # Retry failed Cypher queries              │
│                                                                                     │
│   DEBUG SETTINGS                                                                    │
│   --------------                                                                    │
│   CREATE_GRAPH_IMAGE_ON_INIT = true     # Save LangGraph structure as PNG          │
│                                                                                     │
│   TOOL PHASE MAP                                                                    │
│   --------------                                                                    │
│   TOOL_PHASE_MAP = {                                                               │
│       "query_graph": ["informational", "exploitation", "post_exploitation"],       │
│       "execute_curl": ["informational", "exploitation", "post_exploitation"],      │
│       "execute_naabu": ["informational", "exploitation", "post_exploitation"],     │
│       "metasploit_console": ["exploitation", "post_exploitation"],                 │
│   }                                                                                 │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## File Structure

```
agentic/
├── orchestrator.py      # Main LangGraph orchestrator with ReAct nodes
├── state.py             # State definitions (AgentState, TodoItem, ExecutionStep, etc.)
├── prompts.py           # System prompts for ReAct reasoning
├── tools.py             # Tool definitions (MCP + Neo4j)
├── api.py               # FastAPI REST endpoints (/query, /approve, /health)
├── params.py            # Configuration parameters
├── utils.py             # Utility functions
├── Dockerfile           # Container definition
├── docker-compose.yml   # Service orchestration
└── README.AGENTIC.md    # This documentation
```

---

## Quick Start

```bash
# 1. Start the agent API
cd agentic/
docker-compose up -d

# 2. Start MCP servers (in separate terminals)
cd mcp/
docker-compose up -d

# 3. Start the webapp
cd webapp/
npm run dev

# 4. Open http://localhost:3000/graph and use the AI Assistant drawer
```

---

## Example Session

```
USER: Find and exploit vulnerabilities on 10.0.0.5

AGENT (Iteration 1) [INFORMATIONAL]:
  Thought: I need to first query the graph database for existing information
  Action: query_graph("What vulnerabilities exist on 10.0.0.5?")
  Output: [{"CVE": "CVE-2021-41773", "severity": "critical", "service": "Apache 2.4.49"}]

AGENT (Iteration 2) [INFORMATIONAL]:
  Thought: Found CVE-2021-41773. This is exploitable. I should transition to exploitation phase.
  Action: transition_phase
  Phase Transition: informational -> exploitation
  Reason: Confirmed critical vulnerability CVE-2021-41773 on Apache 2.4.49

[!] AWAITING APPROVAL - User must approve phase transition

USER: [Clicks APPROVE]

AGENT (Iteration 3) [EXPLOITATION]:
  Thought: User approved. Now I can use Metasploit to exploit CVE-2021-41773
  Action: metasploit_console("search CVE-2021-41773")
  Output: exploit/multi/http/apache_normalize_path_rce

AGENT (Iteration 4) [EXPLOITATION]:
  Thought: Found the exploit module. Let me configure it.
  Action: metasploit_console("use exploit/multi/http/apache_normalize_path_rce; set RHOSTS 10.0.0.5; exploit -j")
  Output: [*] Session 1 opened

AGENT (Iteration 5) [EXPLOITATION]:
  Thought: Got a session! Should transition to post-exploitation.
  Action: transition_phase
  Phase Transition: exploitation -> post_exploitation

...
```

---

## Security Considerations

1. **Phase Restrictions**: Dangerous tools (metasploit) are locked behind approval checkpoints
2. **Tenant Isolation**: All Neo4j queries are automatically filtered by user_id and project_id
3. **Session Continuity**: State is isolated per user/project/session combination
4. **Audit Trail**: Full execution trace is maintained for review

---

## References

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [ReAct Pattern Paper](https://arxiv.org/abs/2210.03629)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [Neo4j Graph Database](https://neo4j.com/)
