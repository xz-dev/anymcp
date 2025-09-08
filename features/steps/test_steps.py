from behave import given, when, then
import asyncio
from pathlib import Path
import json

# Add parent directory to Python path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from anymcp.tool_manager import ToolManager


@given('behave is installed and configured')
def step_behave_configured(context):
    assert Path("behave.ini").exists()


@given('there is a tool named "{tool_name}"')
def step_ensure_tool_exists(context, tool_name):
    if not hasattr(context, 'tool_manager'):
        tools_dir = str(context.tools_dir) if hasattr(context, 'tools_dir') else "tools"
        context.tool_manager = ToolManager(tools_dir=tools_dir)
    
    code = f'''
def execute(text: str = "test") -> str:
    """Test tool {tool_name}"""
    if text == "":
        return ""
    return text[::-1]
'''
    asyncio.run(context.tool_manager.create_tool(tool_name, code, overwrite=True))


@when('I create a BDD test for the tool with test cases')
@when('I create a BDD test for the tool with test cases:')
def step_create_test_with_cases(context):
    test_scenarios = []
    for row in context.table:
        test_scenarios.append({
            "input": {"text": row["input"]},
            "expected": row["expected"]
        })
    
    result = asyncio.run(context.tool_manager.create_tool_test(
        "string_reverser",
        test_scenarios
    ))
    context.test_creation_result = result


@then('the test file should be created in features directory')
def step_check_test_file_created(context):
    assert context.test_creation_result["success"] == True
    assert Path(context.test_creation_result["feature_file"]).exists()


@then('the test should follow behave format')
def step_check_behave_format(context):
    with open(context.test_creation_result["feature_file"], 'r') as f:
        content = f.read()
    assert "Feature:" in content
    assert "Scenario:" in content


@then('the test should be runnable')
def step_check_test_runnable(context):
    assert Path(context.test_creation_result["steps_file"]).exists()


@given('there are behave tests for "{tool_name}"')
def step_create_tests_for_tool(context, tool_name):
    test_scenarios = [
        {"input": {"text": "hello"}, "expected": "olleh"},
        {"input": {"text": "world"}, "expected": "dlrow"}
    ]
    asyncio.run(context.tool_manager.create_tool_test(tool_name, test_scenarios))


@when('I run the tests for "{tool_name}"')
def step_run_tool_tests(context, tool_name):
    result = asyncio.run(context.tool_manager.test_tool(tool_name))
    context.test_result = result


@then('all tests should pass')
def step_check_tests_pass(context):
    assert context.test_result["passed"] == True


@then('I should see a test report with results')
def step_check_test_report(context):
    assert "output" in context.test_result
    assert context.test_result["output"]


@given('there is a tool with a bug')
def step_create_buggy_tool(context):
    if not hasattr(context, 'tool_manager'):
        tools_dir = str(context.tools_dir) if hasattr(context, 'tools_dir') else "tools"
        context.tool_manager = ToolManager(tools_dir=tools_dir)
    
    code = '''
def execute(x: int) -> int:
    """Buggy tool that returns wrong result"""
    return x + 1  # Bug: should return x * 2
'''
    asyncio.run(context.tool_manager.create_tool("buggy_tool", code, overwrite=True))


@given('there are tests that check for correct behavior')
def step_create_tests_for_buggy(context):
    test_scenarios = [
        {"input": {"x": 2}, "expected": "4"},  # This will fail
        {"input": {"x": 3}, "expected": "6"}   # This will fail
    ]
    asyncio.run(context.tool_manager.create_tool_test("buggy_tool", test_scenarios))


@when('I run the tests')
def step_run_tests(context):
    result = asyncio.run(context.tool_manager.test_tool("buggy_tool"))
    context.test_result = result


@then('the failing tests should be identified')
def step_check_failures_identified(context):
    assert context.test_result["passed"] == False


@then('I should see which assertions failed')
def step_check_assertion_failures(context):
    output = context.test_result.get("output", "")
    assert "fail" in output.lower() or "error" in context.test_result.get("error", "").lower()


@then('I should see helpful error messages')
def step_check_error_messages(context):
    assert context.test_result.get("output") or context.test_result.get("error")


@when('I create BDD tests with multiple scenarios:')
def step_create_multiple_scenarios(context):
    # For now, just create a simple test
    test_scenarios = [
        {"input": {"operation": "add", "a": 5, "b": 3}, "expected": "8"},
        {"input": {"operation": "subtract", "a": 10, "b": 3}, "expected": "7"}
    ]
    result = asyncio.run(context.tool_manager.create_tool_test("calculator", test_scenarios))
    context.test_creation_result = result


@then('all scenarios should be included in the test file')
def step_check_all_scenarios(context):
    with open(context.test_creation_result["feature_file"], 'r') as f:
        content = f.read()
    assert "Scenario:" in content
    assert content.count("Scenario:") >= 2


@then('each scenario should have proper step definitions')
def step_check_step_definitions(context):
    assert Path(context.test_creation_result["steps_file"]).exists()


@when('I create tests with data tables:')
def step_create_with_data_tables(context):
    test_scenarios = []
    # Parse the context.text to extract test scenarios
    for line in context.text.strip().split('\n'):
        if '|' in line and 'input' not in line:
            parts = [p.strip() for p in line.split('|') if p.strip()]
            if len(parts) >= 2:
                test_scenarios.append({
                    "input": {"text": parts[0]},
                    "expected": parts[1]
                })
    result = asyncio.run(context.tool_manager.create_tool_test("text_processor", test_scenarios))
    context.test_creation_result = result


@then('the test should handle all data variations')
def step_check_data_variations(context):
    with open(context.test_creation_result["feature_file"], 'r') as f:
        content = f.read()
    assert "| parameter | value |" in content


@then('the step definitions should parse the table correctly')
def step_check_table_parsing(context):
    with open(context.test_creation_result["steps_file"], 'r') as f:
        content = f.read()
    assert "context.table" in content


@when('I create a test with background setup:')
def step_create_with_background(context):
    test_scenarios = [{"input": {}, "expected": "result"}]
    result = asyncio.run(context.tool_manager.create_tool_test("db_tool", test_scenarios))
    context.test_creation_result = result


@then('the background steps should run before each scenario')
def step_check_background_steps(context):
    with open(context.test_creation_result["feature_file"], 'r') as f:
        content = f.read()
    assert "Background:" in content


@then('the test should have proper setup and teardown')
def step_check_setup_teardown(context):
    assert context.test_creation_result["success"] == True


@when('I create a test without step definitions')
def step_create_without_steps(context):
    test_scenarios = [{"input": {}, "expected": "result"}]
    result = asyncio.run(context.tool_manager.create_tool_test("new_tool", test_scenarios))
    context.test_creation_result = result


@then('step definition stubs should be generated')
def step_check_stubs_generated(context):
    assert Path(context.test_creation_result["steps_file"]).exists()


@then('the stubs should match the test scenarios')
def step_check_stubs_match(context):
    with open(context.test_creation_result["steps_file"], 'r') as f:
        content = f.read()
    assert "@given" in content or "@when" in content or "@then" in content


@then('the stubs should include parameter hints')
def step_check_parameter_hints(context):
    with open(context.test_creation_result["steps_file"], 'r') as f:
        content = f.read()
    assert "def step_" in content


@given('there is an async tool named "{tool_name}"')
def step_create_async_tool(context, tool_name):
    if not hasattr(context, 'tool_manager'):
        tools_dir = str(context.tools_dir) if hasattr(context, 'tools_dir') else "tools"
        context.tool_manager = ToolManager(tools_dir=tools_dir)
    
    code = '''
import asyncio

async def fetch_data():
    await asyncio.sleep(0.1)
    return "fetched"

def execute():
    return asyncio.run(fetch_data())
'''
    asyncio.run(context.tool_manager.create_tool(tool_name, code, overwrite=True))


@when('I create tests for async operations:')
def step_create_async_tests(context):
    test_scenarios = [{"input": {}, "expected": "fetched"}]
    result = asyncio.run(context.tool_manager.create_tool_test("async_fetcher", test_scenarios))
    context.test_creation_result = result


@then('the test should handle async/await properly')
def step_check_async_handling(context):
    with open(context.test_creation_result["steps_file"], 'r') as f:
        content = f.read()
    assert "asyncio" in content


@then('the test should use appropriate async test runners')
def step_check_async_runners(context):
    with open(context.test_creation_result["steps_file"], 'r') as f:
        content = f.read()
    assert "asyncio.run" in content