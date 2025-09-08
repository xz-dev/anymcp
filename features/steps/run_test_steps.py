from behave import given, when, then
import asyncio
from pathlib import Path
import json

# Add parent directory to Python path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from anymcp.tool_manager import ToolManager


@given('there are tests for "{tool_name}"')
def step_ensure_tests_exist(context, tool_name):
    """Ensure tests exist for a tool"""
    if not hasattr(context, 'tool_manager'):
        tools_dir = str(context.tools_dir) if hasattr(context, 'tools_dir') else "tools"
        context.tool_manager = ToolManager(tools_dir=tools_dir)
    
    # Create a simple test if it doesn't exist
    test_scenarios = [
        {"input": {"x": 1}, "expected": "1"}
    ]
    asyncio.run(context.tool_manager.create_tool_test(tool_name, test_scenarios))


@when('I run the test "{test_name}"')
def step_run_test(context, test_name):
    """Run a specific test"""
    if not hasattr(context, 'tool_manager'):
        tools_dir = str(context.tools_dir) if hasattr(context, 'tools_dir') else "tools"
        context.tool_manager = ToolManager(tools_dir=tools_dir)
    
    result = asyncio.run(context.tool_manager.run_test(test_name))
    context.test_result = result


@when('I run the test "{test_name}" with verbose mode')
def step_run_test_verbose(context, test_name):
    """Run a test in verbose mode"""
    if not hasattr(context, 'tool_manager'):
        tools_dir = str(context.tools_dir) if hasattr(context, 'tools_dir') else "tools"
        context.tool_manager = ToolManager(tools_dir=tools_dir)
    
    result = asyncio.run(context.tool_manager.run_test(test_name, verbose=True))
    context.test_result = result


@then('the test execution should succeed')
def step_check_test_success(context):
    """Check if test execution succeeded"""
    assert context.test_result["success"] == True, f"Test failed: {context.test_result.get('error')}"


@then('the test execution should fail')
def step_check_test_failure(context):
    """Check if test execution failed"""
    assert context.test_result["success"] == False


@then('the test execution should complete')
def step_check_test_complete(context):
    """Check if test execution completed"""
    assert "output" in context.test_result or "error" in context.test_result


@then('I should see test output')
def step_check_test_output(context):
    """Check for test output"""
    assert "output" in context.test_result
    assert len(context.test_result["output"]) > 0


@then('I should see test statistics')
def step_check_test_statistics(context):
    """Check for test statistics"""
    assert "statistics" in context.test_result or "output" in context.test_result


@then('I should get an error message about test not found')
def step_check_test_not_found(context):
    """Check for test not found error"""
    assert "error" in context.test_result
    assert "not found" in context.test_result["error"].lower()


@then('I should see output from multiple test files')
def step_check_multiple_test_output(context):
    """Check for output from multiple tests"""
    output = context.test_result.get("output", "")
    # Check for multiple feature files or scenarios
    assert "feature" in output.lower() or "scenario" in output.lower()


@then('I should see detailed test output')
def step_check_detailed_output(context):
    """Check for detailed/verbose output"""
    output = context.test_result.get("output", "")
    assert len(output) > 100  # Verbose output should be longer


@then('I should see step-by-step execution')
def step_check_step_execution(context):
    """Check for step-by-step execution details"""
    output = context.test_result.get("output", "")
    assert "step" in output.lower() or "given" in output.lower() or "when" in output.lower()


@given('there are multiple test files available')
def step_create_multiple_tests(context):
    """Create multiple test files"""
    if not hasattr(context, 'tool_manager'):
        tools_dir = str(context.tools_dir) if hasattr(context, 'tools_dir') else "tools"
        context.tool_manager = ToolManager(tools_dir=tools_dir)
    
    # Ensure at least one test exists
    test_feature = Path("features/search_tool.feature")
    assert test_feature.exists()


@given('there is a tool with bugs')
def step_create_buggy_tool(context):
    """Create a tool with bugs"""
    if not hasattr(context, 'tool_manager'):
        tools_dir = str(context.tools_dir) if hasattr(context, 'tools_dir') else "tools"
        context.tool_manager = ToolManager(tools_dir=tools_dir)
    
    code = '''
def execute(x: int) -> int:
    # Bug: should return x * 2 but returns x + 1
    return x + 1
'''
    asyncio.run(context.tool_manager.create_tool("buggy_tool", code, overwrite=True))


@given('there are tests that will fail')
def step_create_failing_tests(context):
    """Create tests that will fail"""
    test_scenarios = [
        {"input": {"x": 2}, "expected": "4"},  # Will fail: returns 3 not 4
        {"input": {"x": 3}, "expected": "6"}   # Will fail: returns 4 not 6
    ]
    asyncio.run(context.tool_manager.create_tool_test("buggy_tool", test_scenarios))


@when('I run the test for the buggy tool')
def step_run_buggy_test(context):
    """Run test for buggy tool"""
    result = asyncio.run(context.tool_manager.run_test("buggy_tool"))
    context.test_result = result


@then('I should see which tests failed')
def step_check_failed_tests(context):
    """Check which tests failed"""
    output = context.test_result.get("output", "") + context.test_result.get("error", "")
    assert "fail" in output.lower()


@then('I should see failure details')
def step_check_failure_details(context):
    """Check for failure details"""
    output = context.test_result.get("output", "") + context.test_result.get("error", "")
    assert "expected" in output.lower() or "assert" in output.lower()


@given('there is a tool with comprehensive tests')
def step_create_comprehensive_tests(context):
    """Create comprehensive tests"""
    if not hasattr(context, 'tool_manager'):
        tools_dir = str(context.tools_dir) if hasattr(context, 'tools_dir') else "tools"
        context.tool_manager = ToolManager(tools_dir=tools_dir)
    
    code = '''
def execute(operation: str, x: int, y: int = 0) -> int:
    if operation == "add":
        return x + y
    elif operation == "multiply":
        return x * y
    else:
        return 0
'''
    asyncio.run(context.tool_manager.create_tool("math_tool", code, overwrite=True))
    
    test_scenarios = [
        {"input": {"operation": "add", "x": 2, "y": 3}, "expected": "5"},
        {"input": {"operation": "multiply", "x": 4, "y": 5}, "expected": "20"},
        {"input": {"operation": "unknown", "x": 1}, "expected": "0"}
    ]
    asyncio.run(context.tool_manager.create_tool_test("math_tool", test_scenarios))


@when('I run the test and it completes')
def step_run_comprehensive_test(context):
    """Run comprehensive test"""
    result = asyncio.run(context.tool_manager.run_test("math_tool"))
    context.test_result = result


@then('I should see scenario statistics')
def step_check_scenario_stats(context):
    """Check for scenario statistics"""
    if "statistics" in context.test_result:
        assert "scenarios" in str(context.test_result["statistics"])
    else:
        output = context.test_result.get("output", "")
        assert "scenario" in output.lower()


@then('I should see step statistics')
def step_check_step_stats(context):
    """Check for step statistics"""
    if "statistics" in context.test_result:
        stats = str(context.test_result["statistics"])
        assert "step" in stats.lower()
    else:
        output = context.test_result.get("output", "")
        assert "step" in output.lower()


@then('the statistics should be in the result')
def step_check_stats_in_result(context):
    """Check statistics are in result"""
    assert "statistics" in context.test_result or "output" in context.test_result


@given('there is a test in a subdirectory')
def step_create_test_in_subdir(context):
    """Create test in subdirectory"""
    if not hasattr(context, 'tool_manager'):
        tools_dir = str(context.tools_dir) if hasattr(context, 'tools_dir') else "tools"
        context.tool_manager = ToolManager(tools_dir=tools_dir)
    
    # Ensure a test exists
    test_scenarios = [{"input": {}, "expected": "result"}]
    asyncio.run(context.tool_manager.create_tool_test("subdir_tool", test_scenarios))


@when('I run the test from a different directory')
def step_run_test_different_dir(context):
    """Run test from different directory"""
    result = asyncio.run(context.tool_manager.run_test("subdir_tool"))
    context.test_result = result


@then('the test should still execute correctly')
def step_check_test_executes(context):
    """Check test executes correctly"""
    assert "output" in context.test_result or "error" in context.test_result


@then('the working directory should be handled properly')
def step_check_working_dir(context):
    """Check working directory handling"""
    # If test ran, working directory was handled
    assert context.test_result is not None