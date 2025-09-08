# Changelog

## [0.1.0] - 2024-01-09

### Added
- Initial release of AnyMCP - Self-Creating MCP Tool System
- Core functionality for AI to create, test, and manage its own tools
- BDD-driven development with behave framework
- 8 core MCP functions:
  - `search_tool` - Search for available tools with keyword filtering
  - `execute_tool` - Execute Python tools with parameters and timeout control
  - `create_tool` - Create new tools from Python code with validation
  - `create_tool_test` - Generate BDD tests for tools automatically
  - `test_tool` - Run BDD tests for specific tools
  - `run_test` - Run any test file or all tests with statistics
  - `shell_command` - Execute shell commands with safety checks
  - `list_tools` - List all available tools in the tools directory
- Comprehensive BDD test coverage with 7 feature files
- Example tools (calculator, string_reverser)
- MCP server implementation compatible with Claude Desktop
- Modern Python practices using pathlib and argparse
- Safety features for dangerous command prevention
- Timeout control for long-running operations

### Security
- Input validation for tool creation
- Dangerous shell command blocking
- Path traversal prevention in tool names

### Documentation
- Complete README with usage examples
- BDD test scenarios in Gherkin format
- Code documentation and type hints