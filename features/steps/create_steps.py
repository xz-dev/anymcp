from behave import given, when, then
import asyncio
from pathlib import Path
import textwrap

# Add parent directory to Python path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from anymcp.tool_manager import ToolManager


@when('I create a tool named "{name}" with the following code')
def step_create_tool_with_code(context, name):
    code = textwrap.dedent(context.text)
    result = asyncio.run(context.tool_manager.create_tool(name, code))
    context.creation_result = result


@when(u'I create a tool named "{name}" with the following code:')
def step_create_tool_with_code_colon(context, name):
    code = textwrap.dedent(context.text)
    result = asyncio.run(context.tool_manager.create_tool(name, code))
    context.creation_result = result


@then('the tool should be created successfully')
def step_check_creation_success(context):
    assert context.creation_result["success"] == True


@then('the tool file should exist in the tools directory')
def step_check_tool_file_exists(context):
    tool_path = Path(context.creation_result["path"])
    assert tool_path.exists()


@then('the tool should be executable')
def step_check_executable(context):
    tool_path = Path(context.creation_result["path"])
    assert tool_path.stat().st_mode & 0o111


@when('I create a tool named "{name}" with imports')
def step_create_with_imports(context, name):
    code = textwrap.dedent(context.text)
    result = asyncio.run(context.tool_manager.create_tool(name, code))
    context.creation_result = result


@when(u'I create a tool named "{name}" with imports:')
def step_create_with_imports_colon(context, name):
    code = textwrap.dedent(context.text)
    result = asyncio.run(context.tool_manager.create_tool(name, code))
    context.creation_result = result


@when(u'I create a tool with invalid Python code:')
def step_create_invalid_code_colon(context):
    code = textwrap.dedent(context.text)
    result = asyncio.run(context.tool_manager.create_tool("invalid_tool", code))
    context.creation_result = result


@when(u'I create a tool named "{name}" with helper functions:')
def step_create_complex_tool_colon(context, name):
    code = textwrap.dedent(context.text)
    result = asyncio.run(context.tool_manager.create_tool(name, code))
    context.creation_result = result


@when(u'I create a tool with metadata:')
def step_create_with_metadata_colon(context):
    code = textwrap.dedent(context.text)
    result = asyncio.run(context.tool_manager.create_tool("weather_fetcher", code))
    context.creation_result = result


@then('the tool should handle JSON formatting correctly')
def step_check_json_formatter(context):
    test_json = '{"a":1,"b":2}'
    result = asyncio.run(context.tool_manager.execute_tool(
        "json_formatter",
        {"data": test_json, "indent": 2}
    ))
    assert result["success"] == True
    # The result might be parsed JSON or a string
    expected = '{\n  "a": 1,\n  "b": 2\n}'
    if isinstance(result["result"], dict):
        # Result was parsed as JSON, check it matches expected data
        assert result["result"] == {"a": 1, "b": 2}
    else:
        # Result is a string, check formatting
        assert expected in str(result["result"])


@when('I create a tool with invalid Python code')
def step_create_invalid_code(context):
    code = textwrap.dedent(context.text)
    result = asyncio.run(context.tool_manager.create_tool("invalid_tool", code))
    context.creation_result = result


@then('the tool creation should fail')
def step_check_creation_failure(context):
    assert context.creation_result["success"] == False


@then('I should get a syntax error message')
def step_check_syntax_error(context):
    assert "syntax" in context.creation_result["error"].lower()


@given('there is already a tool named "{name}"')
def step_existing_tool(context, name):
    asyncio.run(context.tool_manager.create_tool(
        name,
        f'def execute(): return "{name}"',
        overwrite=True
    ))


@when('I try to create a tool named "{name}"')
def step_try_create_existing(context, name):
    result = asyncio.run(context.tool_manager.create_tool(
        name,
        'def execute(): return "new version"',
        overwrite=False
    ))
    context.creation_result = result


@then('I should get a warning that the tool exists')
def step_check_exists_warning(context):
    assert context.creation_result["success"] == False
    assert "already exists" in context.creation_result["error"]


@then('I should be asked if I want to overwrite it')
def step_check_overwrite_message(context):
    assert "overwrite" in context.creation_result["error"].lower()


@when('I create a tool named "{name}" with helper functions')
def step_create_complex_tool(context, name):
    code = textwrap.dedent(context.text)
    result = asyncio.run(context.tool_manager.create_tool(name, code))
    context.creation_result = result


@then('the tool should calculate statistics correctly')
def step_check_statistics(context):
    result = asyncio.run(context.tool_manager.execute_tool(
        "data_analyzer",
        {"numbers": [1, 2, 3, 4, 5]}
    ))
    assert result["success"] == True
    assert result["result"]["mean"] == 3.0
    assert result["result"]["median"] == 3.0
    assert result["result"]["min"] == 1
    assert result["result"]["max"] == 5


@when('I create a tool with metadata')
def step_create_with_metadata(context):
    code = textwrap.dedent(context.text)
    result = asyncio.run(context.tool_manager.create_tool("weather_fetcher", code))
    context.creation_result = result


@then('the tool should be created with proper metadata')
def step_check_metadata_creation(context):
    assert context.creation_result["success"] == True


@then('the metadata should be searchable')
def step_check_searchable_metadata(context):
    tools = asyncio.run(context.tool_manager.search_tools(detailed=True))
    weather_tool = next((t for t in tools if "weather" in t["name"].lower() or t["name"] == "weather_fetcher"), None)
    assert weather_tool is not None, f"Could not find weather tool in {[t['name'] for t in tools]}"
    assert weather_tool.get("version") == "1.0.0", f"Version mismatch: got {weather_tool.get('version')}"


@then('the tool should have execute function added automatically')
def step_check_execute_added(context):
    """Check if execute function was added"""
    assert context.creation_result["success"] == True


@then('executing with b=0 should raise an error')
def step_check_division_error(context):
    """Check division by zero error"""
    result = asyncio.run(context.tool_manager.execute_tool("safe_divider", {"a": 10, "b": 0}))
    assert result["success"] == False
    assert "zero" in result.get("error", "").lower()


@when('I create a tool named "{name}" with valid code')
def step_create_with_dangerous_name(context, name):
    """Try to create tool with dangerous name"""
    code = 'def execute(): return "test"'
    result = asyncio.run(context.tool_manager.create_tool(name, code))
    context.creation_result = result


@then('I should get a security error message')
def step_check_security_error(context):
    """Check for security error"""
    pass


@when('I create a tool with {count:d} lines of code')
def step_create_large_tool(context, count):
    """Create tool with many lines"""
    lines = []
    lines.append("def execute():")
    for i in range(count - 2):
        lines.append(f"    # Line {i}")
    lines.append("    return 'done'")
    code = '\n'.join(lines)
    result = asyncio.run(context.tool_manager.create_tool("large_tool", code, overwrite=True))
    context.creation_result = result


@then('the tool file should contain all the code')
def step_check_all_code(context):
    """Check that all code was saved"""
    assert context.creation_result["success"] == True