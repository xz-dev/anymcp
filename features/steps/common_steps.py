from behave import given, when, then
import asyncio
import json
from pathlib import Path

# Add parent directory to Python path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from anymcp.tool_manager import ToolManager


@given('the MCP tool system is initialized')
def step_initialize_mcp(context):
    # Use the test-specific tools directory from environment.py
    tools_dir = str(context.tools_dir) if hasattr(context, 'tools_dir') else "tools"
    context.tool_manager = ToolManager(tools_dir=tools_dir)
    context.results = []


@given('there are example tools in the tools directory')
def step_create_example_tools(context):
    # Ensure we have the tool_manager initialized with test directory
    if not hasattr(context, 'tool_manager'):
        tools_dir = str(context.tools_dir) if hasattr(context, 'tools_dir') else "tools"
        context.tool_manager = ToolManager(tools_dir=tools_dir)
    
    asyncio.run(context.tool_manager.create_tool(
        "string_reverser",
        '''
def execute(text: str) -> str:
    """Reverses a string"""
    return text[::-1]
''',
        overwrite=True
    ))
    
    asyncio.run(context.tool_manager.create_tool(
        "calculator",
        '''
def execute(operation: str, a: float, b: float) -> float:
    """Simple calculator"""
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
    else:
        raise ValueError(f"Unknown operation: {operation}")
''',
        overwrite=True
    ))


@given('the tools directory is empty')
def step_empty_tools_dir(context):
    # Use the test-specific tools directory
    tools_dir = context.tools_dir if hasattr(context, 'tools_dir') else Path("tools")
    if tools_dir.exists():
        for file in tools_dir.glob("*.py"):
            file.unlink()


@given('the tools directory is writable')
def step_tools_dir_writable(context):
    # Use the test-specific tools directory
    tools_dir = context.tools_dir if hasattr(context, 'tools_dir') else Path("tools")
    tools_dir.mkdir(exist_ok=True)
    # Check if directory is writable by trying to create a temp file
    try:
        test_file = tools_dir / ".write_test"
        test_file.touch()
        test_file.unlink()
        assert True
    except:
        assert False, "Tools directory is not writable"


@when('I search for tools without any filter')
def step_search_all_tools(context):
    result = asyncio.run(context.tool_manager.search_tools())
    context.results.append(result)


@when('I search for tools with keyword "{keyword}"')
def step_search_with_keyword(context, keyword):
    result = asyncio.run(context.tool_manager.search_tools(keyword=keyword))
    context.results.append(result)
    context.search_keyword = keyword


@when('I search for tools with detailed information')
def step_search_detailed(context):
    result = asyncio.run(context.tool_manager.search_tools(detailed=True))
    context.results.append(result)


@then('I should see a list of all available tools')
def step_check_tools_list(context):
    result = context.results[-1]
    assert isinstance(result, list)
    assert len(result) > 0


@then('each tool should have a name and description')
def step_check_tool_fields(context):
    result = context.results[-1]
    for tool in result:
        assert "name" in tool
        assert "description" in tool


@then('I should only see tools that match the keyword')
def step_check_keyword_match(context):
    result = context.results[-1]
    keyword = getattr(context, 'search_keyword', context.text or "file")
    for tool in result:
        name_match = keyword.lower() in tool["name"].lower()
        desc_match = keyword.lower() in tool.get("description", "").lower()
        assert name_match or desc_match, f"Tool '{tool['name']}' doesn't match keyword '{keyword}'"


@then('I should get an empty result')
def step_check_empty_result(context):
    result = context.results[-1]
    assert isinstance(result, list)
    assert len(result) == 0


@then('I should receive a message that no tools are available')
def step_no_tools_message(context):
    pass


@then('I should see tool names')
def step_check_tool_names(context):
    result = context.results[-1]
    for tool in result:
        assert "name" in tool
        assert tool["name"]


@then('I should see tool descriptions')
def step_check_descriptions(context):
    result = context.results[-1]
    for tool in result:
        assert "description" in tool


@then('I should see tool parameters')
def step_check_parameters(context):
    result = context.results[-1]
    for tool in result:
        assert "parameters" in tool


@then('I should see tool file paths')
def step_check_paths(context):
    result = context.results[-1]
    for tool in result:
        assert "path" in tool
        assert Path(tool["path"]).exists()


@then('the results should include matching tool names or descriptions')
def step_check_matching_results(context):
    result = context.results[-1]
    assert len(result) > 0


@when('I search for tools')
def step_search_tools(context):
    result = asyncio.run(context.tool_manager.search_tools())
    context.results.append(result)


@given('the "{tool_name}" tool is available')
def step_tool_available(context, tool_name):
    # Initialize tool manager if needed
    if not hasattr(context, 'tool_manager'):
        tools_dir = str(context.tools_dir) if hasattr(context, 'tools_dir') else "tools"
        context.tool_manager = ToolManager(tools_dir=tools_dir)
    
    # Create the tool
    code = f'''
def execute(x: int = 1) -> int:
    return x
'''
    asyncio.run(context.tool_manager.create_tool(tool_name, code, overwrite=True))
    context.tool_name = tool_name


@when('I execute "{tool_name}" with parameters:')
def step_execute_with_params(context, tool_name):
    params = {}
    for row in context.table:
        params[row["parameter"]] = row["value"]
        # Try to convert to appropriate type
        try:
            params[row["parameter"]] = int(row["value"])
        except ValueError:
            try:
                params[row["parameter"]] = float(row["value"])
            except ValueError:
                pass  # Keep as string
    
    result = asyncio.run(context.tool_manager.execute_tool(tool_name, params))
    context.result = result


@then('the result should be "{expected}"')
def step_check_result(context, expected):
    assert context.result["success"], f"Tool execution failed: {context.result}"
    assert str(context.result["result"]) == expected, f"Expected {expected}, got {context.result['result']}"


@then('an error should occur with message "{message}"')
def step_check_error(context, message):
    assert not context.result["success"], "Expected an error but tool succeeded"
    assert message in context.result["error"], f"Expected error '{message}', got '{context.result['error']}"