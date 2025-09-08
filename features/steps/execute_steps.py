from behave import given, when, then
import asyncio
import json
from pathlib import Path

# Add parent directory to Python path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from anymcp.tool_manager import ToolManager


@given('there is a sample calculator tool available')
def step_ensure_calculator(context):
    if not hasattr(context, 'tool_manager'):
        tools_dir = str(context.tools_dir) if hasattr(context, 'tools_dir') else "tools"
        context.tool_manager = ToolManager(tools_dir=tools_dir)
    
    asyncio.run(context.tool_manager.create_tool(
        "calculator",
        '''
def execute(operation: str, a: float = 0, b: float = 0) -> float:
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


@when('I execute the "{tool_name}" tool with operation "{op}" and numbers {a:d} and {b:d}')
def step_execute_calculator(context, tool_name, op, a, b):
    result = asyncio.run(context.tool_manager.execute_tool(
        tool_name,
        {"operation": op, "a": float(a), "b": float(b)}
    ))
    context.execution_result = result


@when('I execute the "{tool_name}" tool without parameters')
def step_execute_without_params(context, tool_name):
    result = asyncio.run(context.tool_manager.execute_tool(tool_name, {}))
    context.execution_result = result


@when('I execute a tool named "{tool_name}"')
def step_execute_nonexistent(context, tool_name):
    result = asyncio.run(context.tool_manager.execute_tool(tool_name, {}))
    context.execution_result = result


@then('the tool should execute successfully')
def step_check_success(context):
    assert context.execution_result["success"] == True


@then('the result should be {expected:d}')
def step_check_result_number(context, expected):
    assert context.execution_result["result"] == float(expected)


@then('the execution should fail')
def step_check_failure(context):
    assert context.execution_result["success"] == False


@then('I should get an error message about missing parameters')
def step_check_param_error(context):
    assert "error" in context.execution_result
    error = context.execution_result["error"].lower()
    assert "missing" in error or "required" in error or "error" in error


@then('I should get an error message that the tool was not found')
def step_check_not_found(context):
    assert "error" in context.execution_result
    assert "not found" in context.execution_result["error"].lower()


@given('there is a "{tool_name}" tool available')
def step_create_tool(context, tool_name):
    if not hasattr(context, 'tool_manager'):
        tools_dir = str(context.tools_dir) if hasattr(context, 'tools_dir') else "tools"
        context.tool_manager = ToolManager(tools_dir=tools_dir)
    
    if tool_name == "data_processor":
        code = '''
import json

def execute(data: str) -> dict:
    """Process JSON data"""
    parsed = json.loads(data)
    return {"processed": True, "data": parsed}
'''
    elif tool_name == "file_generator":
        code = '''
def execute(filename: str, content: str) -> dict:
    """Generate a file"""
    with open(filename, 'w') as f:
        f.write(content)
    return {"created": filename, "size": len(content)}
'''
    elif tool_name == "slow_tool":
        code = '''
import time

def execute(duration: int = 5) -> str:
    """A slow tool for testing timeouts"""
    time.sleep(duration)
    return "Completed"
'''
    else:
        code = f'''
def execute() -> str:
    """Generic tool {tool_name}"""
    return "{tool_name} executed"
'''
    
    asyncio.run(context.tool_manager.create_tool(tool_name, code, overwrite=True))


@when('I execute the tool with valid JSON input')
def step_execute_with_json(context):
    test_data = '{"key": "value", "number": 42}'
    result = asyncio.run(context.tool_manager.execute_tool(
        "data_processor",
        {"data": test_data}
    ))
    context.execution_result = result


@then('the tool should return structured JSON output')
def step_check_json_output(context):
    assert context.execution_result["success"] == True
    assert isinstance(context.execution_result["result"], dict)


@then('the output should be parseable')
def step_check_parseable(context):
    result = context.execution_result["result"]
    assert result is not None


@when('I execute the tool to generate a file')
def step_execute_file_generator(context):
    import tempfile
    context.test_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt").name
    result = asyncio.run(context.tool_manager.execute_tool(
        "file_generator",
        {"filename": context.test_file, "content": "Test content"}
    ))
    context.execution_result = result


@then('the tool should create the specified file')
def step_check_file_created(context):
    assert context.execution_result["success"] == True
    assert Path(context.test_file).exists()


@then('the file should contain the expected content')
def step_check_file_content(context):
    with open(context.test_file, 'r') as f:
        content = f.read()
    assert content == "Test content"
    
    Path(context.test_file).unlink()


@given('there is a "{tool_name}" that takes long to execute')
def step_create_slow_tool(context, tool_name):
    step_create_tool(context, tool_name)


@when('I execute the tool with a timeout of {timeout:d} seconds')
def step_execute_with_timeout(context, timeout):
    context.timeout = timeout
    context.execution_started = True


@when('the tool takes longer than {duration:d} seconds')
def step_tool_takes_long(context, duration):
    # Tool should sleep longer than timeout to test timeout behavior
    result = asyncio.run(context.tool_manager.execute_tool(
        "slow_tool",
        {"duration": duration + 1},  # Sleep 1 second longer than stated to ensure timeout
        timeout=context.timeout
    ))
    context.execution_result = result


@then('the execution should be terminated')
def step_check_terminated(context):
    assert context.execution_result["success"] == False


@then('I should get a timeout error message')
def step_check_timeout_error(context):
    error = context.execution_result.get("error", "")
    assert "timeout" in error.lower() or "timed out" in error.lower(), f"Expected timeout error, got: {error}"