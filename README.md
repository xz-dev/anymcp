# AnyMCP - Self-Creating MCP Tool System

AnyMCP is a BDD-driven MCP (Model Context Protocol) tool system that allows AI to autonomously create, test, and manage its own tools.

## Features

### Core Functions

1. **search_tool** - Search available tools
   - Keyword search support
   - Return detailed tool information
   - Display tool parameters and metadata

2. **execute_tool** - Execute tools
   - Dynamic Python tool execution
   - Parameter passing support
   - Timeout control

3. **create_tool** - Create new tools
   - Create tools using Python code
   - Automatic execution wrapper
   - Syntax validation

4. **create_tool_test** - Create BDD tests for tools
   - Auto-generate behave test files
   - Create step definitions
   - Support multiple test scenarios

5. **test_tool** - Run BDD tests for a specific tool
   - Execute behave tests for a tool
   - Return test results
   - Support verbose output mode

6. **run_test** - Run any test file or all tests
   - Run specific test files by name
   - Run all tests with 'all' parameter
   - Parse and return test statistics

7. **shell_command** - Execute shell commands
   - Run shell commands in project directory
   - Configurable timeout
   - Safety checks for dangerous commands
   - Support custom working directory

8. **list_tools** - List all available tools
   - Show all tools in the tools directory
   - Return tool count and storage location

## Installation

```bash
# Clone repository
git clone <repository>
cd anymcp

# Install dependencies with uv
uv sync
```

## Usage

### Run as MCP Server

```bash
uv run python -m anymcp
```

### Configure in Claude Desktop

Edit Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "anymcp": {
      "command": "uv",
      "args": ["run", "python", "-m", "anymcp"],
      "cwd": "/path/to/anymcp"
    }
  }
}
```

## Example Tools

### Simple Tool

```python
# String reversal tool
def execute(text: str) -> str:
    return text[::-1]
```

### Tool with Metadata

```python
__tool_name__ = "Calculator"
__description__ = "Performs basic arithmetic"
__version__ = "1.0.0"
__parameters__ = {
    "operation": {"type": "string", "required": True},
    "a": {"type": "number", "required": True},
    "b": {"type": "number", "required": True}
}

def execute(operation: str, a: float, b: float) -> float:
    if operation == "add":
        return a + b
    elif operation == "subtract":
        return a - b
    elif operation == "multiply":
        return a * b
    elif operation == "divide":
        if b == 0:
            raise ValueError("Division by zero")
        return a / b
```

## BDD Testing

The project uses behave framework for BDD testing:

```bash
# Run all tests
uv run behave

# Run specific feature tests
uv run behave features/search_tool.feature

# Verbose output mode
uv run behave -v

# Show test summary
uv run behave --summary
```

## Project Structure

```
anymcp/
├── anymcp/              # Main source code
│   ├── __init__.py
│   ├── __main__.py      # Entry point
│   ├── server.py        # MCP server implementation
│   └── tool_manager.py  # Tool management core logic
├── features/            # BDD test feature files
│   ├── steps/          # Step definitions
│   ├── *.feature       # Test scenarios in Gherkin format
│   └── environment.py  # Behave environment configuration
├── tools/              # Tool storage directory (all created tools stored here)
│   └── *.py           # Python tool scripts (executable Python files)
├── pyproject.toml      # Project configuration
├── behave.ini         # Behave configuration
└── README.md
```

## Development Guide

### Adding New Features

1. Write BDD test scenarios in `features/`
2. Implement step definitions in `features/steps/`
3. Implement functionality in `anymcp/tool_manager.py`
4. Add MCP interface in `anymcp/server.py`
5. Run tests to verify functionality

### Tool Development Standards

Each tool must:
- Include an `execute()` function as entry point
- Handle parameter validation
- Return serializable results (string, number, dict, list)
- Include proper error handling

### Modern Python Practices

The project uses modern Python approaches:
- `pathlib.Path` instead of `os.path`
- `argparse` instead of direct `sys.argv` access
- `asyncio` for asynchronous operations
- Type hints for better code documentation

## Example Usage

```python
import asyncio
from anymcp.tool_manager import ToolManager

async def main():
    tool_manager = ToolManager()
    
    # List all available tools
    tools = tool_manager.list_tools()
    print(f"Available tools: {tools}")
    
    # Search for tools by keyword
    tools = await tool_manager.search_tools(keyword="text")
    
    # Create a new tool
    code = '''
def execute(text: str) -> str:
    return text.upper()
'''
    await tool_manager.create_tool("uppercase", code)
    
    # Execute the tool
    result = await tool_manager.execute_tool(
        "uppercase",
        {"text": "hello world"}
    )
    print(result)  # {"success": True, "result": "HELLO WORLD"}
    
    # Run shell commands
    cmd_result = await tool_manager.shell_command("ls -la tools/")
    print(cmd_result["stdout"])
    
    # Create and run tests
    test_scenarios = [
        {"input": {"text": "test"}, "expected": "TEST"}
    ]
    await tool_manager.create_tool_test("uppercase", test_scenarios)
    test_result = await tool_manager.run_test("uppercase")
    print(f"Test passed: {test_result['success']}")

asyncio.run(main())
```

## Tool Storage

All created tools are stored in the `tools/` directory as executable Python scripts. Each tool:
- Is a standalone Python file that can be run directly
- Contains an `execute()` function as the main entry point
- Can include metadata like `__tool_name__`, `__description__`, `__version__`
- Is automatically wrapped with argument parsing if needed

## License

MIT License