import asyncio
from mcp.server import Server, InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ServerCapabilities
from typing import Any, Dict
import json
import sys

from .tool_manager import ToolManager


def main():
    """Main entry point for the MCP server"""
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        print("\nServer stopped by user", file=sys.stderr)
    except Exception as e:
        print(f"Server error: {e}", file=sys.stderr)
        sys.exit(1)


async def run_server():
    """Run the MCP server"""
    server = Server("anymcp")
    tool_manager = ToolManager()
    
    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name="search_tool",
                description="Search for available MCP tools",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "keyword": {
                            "type": "string",
                            "description": "Optional keyword to filter tools"
                        },
                        "detailed": {
                            "type": "boolean",
                            "description": "Return detailed information about tools",
                            "default": False
                        }
                    }
                }
            ),
            Tool(
                name="execute_tool",
                description="Execute an MCP tool with parameters",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "tool_name": {
                            "type": "string",
                            "description": "Name of the tool to execute"
                        },
                        "parameters": {
                            "type": "object",
                            "description": "Parameters to pass to the tool"
                        },
                        "timeout": {
                            "type": "integer",
                            "description": "Execution timeout in seconds",
                            "default": 30
                        }
                    },
                    "required": ["tool_name"]
                }
            ),
            Tool(
                name="create_tool",
                description="Create a new MCP tool using Python code",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name of the tool to create"
                        },
                        "code": {
                            "type": "string",
                            "description": "Python code for the tool (must contain execute function)"
                        },
                        "overwrite": {
                            "type": "boolean",
                            "description": "Whether to overwrite existing tool",
                            "default": False
                        }
                    },
                    "required": ["name", "code"]
                }
            ),
            Tool(
                name="create_tool_test",
                description="Create BDD tests for a tool using behave framework",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "tool_name": {
                            "type": "string",
                            "description": "Name of the tool to test"
                        },
                        "test_scenarios": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "input": {
                                        "type": "object",
                                        "description": "Input parameters for the test"
                                    },
                                    "expected": {
                                        "type": "string",
                                        "description": "Expected output"
                                    },
                                    "error": {
                                        "type": "string",
                                        "description": "Expected error message"
                                    }
                                }
                            },
                            "description": "List of test scenarios"
                        }
                    },
                    "required": ["tool_name", "test_scenarios"]
                }
            ),
            Tool(
                name="test_tool",
                description="Run BDD tests for a tool to verify it works correctly",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "tool_name": {
                            "type": "string",
                            "description": "Name of the tool to test"
                        },
                        "verbose": {
                            "type": "boolean",
                            "description": "Show detailed test output",
                            "default": False
                        }
                    },
                    "required": ["tool_name"]
                }
            ),
            Tool(
                name="run_test",
                description="Run any test file or all tests",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "test_name": {
                            "type": "string",
                            "description": "Name of test file or 'all' to run all tests"
                        },
                        "verbose": {
                            "type": "boolean",
                            "description": "Show detailed test output",
                            "default": False
                        }
                    },
                    "required": ["test_name"]
                }
            ),
            Tool(
                name="shell_command",
                description="Execute a shell command in the project directory",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "Shell command to execute"
                        },
                        "timeout": {
                            "type": "integer",
                            "description": "Command timeout in seconds",
                            "default": 30
                        },
                        "cwd": {
                            "type": "string",
                            "description": "Working directory for command execution"
                        }
                    },
                    "required": ["command"]
                }
            ),
            Tool(
                name="list_tools",
                description="List all available tools in the tools directory",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            )
        ]
    
    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> list[TextContent]:
        try:
            if name == "search_tool":
                keyword = arguments.get("keyword")
                detailed = arguments.get("detailed", False)
                result = await tool_manager.search_tools(keyword, detailed)
                
            elif name == "execute_tool":
                tool_name = arguments["tool_name"]
                parameters = arguments.get("parameters", {})
                timeout = arguments.get("timeout", 30)
                result = await tool_manager.execute_tool(tool_name, parameters, timeout)
                
            elif name == "create_tool":
                name = arguments["name"]
                code = arguments["code"]
                overwrite = arguments.get("overwrite", False)
                result = await tool_manager.create_tool(name, code, overwrite)
                
            elif name == "create_tool_test":
                tool_name = arguments["tool_name"]
                test_scenarios = arguments["test_scenarios"]
                result = await tool_manager.create_tool_test(tool_name, test_scenarios)
                
            elif name == "test_tool":
                tool_name = arguments["tool_name"]
                verbose = arguments.get("verbose", False)
                result = await tool_manager.test_tool(tool_name, verbose)
                
            elif name == "run_test":
                test_name = arguments["test_name"]
                verbose = arguments.get("verbose", False)
                result = await tool_manager.run_test(test_name, verbose)
                
            elif name == "shell_command":
                command = arguments["command"]
                timeout = arguments.get("timeout", 30)
                cwd = arguments.get("cwd")
                result = await tool_manager.shell_command(command, timeout, cwd)
                
            elif name == "list_tools":
                tools = tool_manager.list_tools()
                result = {
                    "success": True,
                    "tools": tools,
                    "count": len(tools),
                    "tools_directory": str(tool_manager.tools_dir)
                }
                
            else:
                result = {"error": f"Unknown tool: {name}"}
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=json.dumps({"error": str(e)}, indent=2)
            )]
    
    # Create initialization options
    init_options = InitializationOptions(
        server_name="anymcp",
        server_version="1.0.0",
        capabilities=ServerCapabilities(
            tools={}  # We support tools
        )
    )
    
    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, init_options)