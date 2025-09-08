from behave import given, when, then
import asyncio
from pathlib import Path
import tempfile
import shutil

# Add parent directory to Python path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from anymcp.tool_manager import ToolManager


@when(u'I execute the shell command "{command}"')
def step_execute_shell_command(context, command):
    """Execute a shell command"""
    if not hasattr(context, 'tool_manager'):
        tools_dir = str(context.tools_dir) if hasattr(context, 'tools_dir') else "tools"
        context.tool_manager = ToolManager(tools_dir=tools_dir)
    
    result = asyncio.run(context.tool_manager.shell_command(command))
    context.shell_result = result


@when('I execute the shell command "{command}" with timeout {timeout:d} seconds')
def step_execute_command_with_timeout(context, command, timeout):
    """Execute command with specific timeout"""
    if not hasattr(context, 'tool_manager'):
        tools_dir = str(context.tools_dir) if hasattr(context, 'tools_dir') else "tools"
        context.tool_manager = ToolManager(tools_dir=tools_dir)
    
    result = asyncio.run(context.tool_manager.shell_command(command, timeout=timeout))
    context.shell_result = result


@when('I execute "{command}" in the directory "{directory}"')
def step_execute_command_in_directory(context, command, directory):
    """Execute command in specific directory"""
    if not hasattr(context, 'tool_manager'):
        tools_dir = str(context.tools_dir) if hasattr(context, 'tools_dir') else "tools"
        context.tool_manager = ToolManager(tools_dir=tools_dir)
    
    # Create directory if needed for test
    Path(directory).mkdir(parents=True, exist_ok=True)
    
    result = asyncio.run(context.tool_manager.shell_command(command, cwd=directory))
    context.shell_result = result
    
    # Clean up test directory
    if directory.startswith("/tmp/test_"):
        shutil.rmtree(directory, ignore_errors=True)


@then('the command should execute successfully')
def step_check_command_success(context):
    """Check if command executed successfully"""
    assert context.shell_result["success"] == True, f"Command failed: {context.shell_result.get('error')}"


@then('the command should fail')
def step_check_command_failure(context):
    """Check if command failed"""
    assert context.shell_result["success"] == False


@then('the command should timeout')
def step_check_command_timeout(context):
    """Check if command timed out"""
    assert context.shell_result["success"] == False
    error = context.shell_result.get("error", "").lower()
    assert "timed out" in error or "timeout" in error, f"Expected timeout error, got: {error}"


@then('the command should be blocked')
def step_check_command_blocked(context):
    """Check if dangerous command was blocked"""
    assert context.shell_result["success"] == False
    assert "dangerous" in context.shell_result.get("error", "").lower()


@then('the stdout should contain "{text}"')
def step_check_stdout_contains(context, text):
    """Check if stdout contains text"""
    stdout = context.shell_result.get("stdout", "")
    assert text in stdout, f"Expected '{text}' in stdout, got: {stdout}"


@then('the stdout should not contain "{text}"')
def step_check_stdout_not_contains(context, text):
    """Check if stdout doesn't contain text"""
    stdout = context.shell_result.get("stdout", "")
    assert text not in stdout, f"Unexpected '{text}' found in stdout: {stdout}"


@then('the stderr should contain error message')
def step_check_stderr_has_error(context):
    """Check if stderr contains error message"""
    stderr = context.shell_result.get("stderr", "")
    assert len(stderr) > 0, "Expected error message in stderr"


@then('the stderr should contain "{text}" or "{alternative}"')
def step_check_stderr_contains_either(context, text, alternative):
    """Check if stderr contains one of two texts"""
    stderr = context.shell_result.get("stderr", "")
    assert text in stderr or alternative in stderr, f"Expected '{text}' or '{alternative}' in stderr"


@then('the exit code should be {code:d}')
def step_check_exit_code(context, code):
    """Check exit code"""
    assert context.shell_result.get("exit_code") == code


@then('the exit code should not be {code:d}')
def step_check_exit_code_not(context, code):
    """Check exit code is not a value"""
    assert context.shell_result.get("exit_code") != code


@then('I should get a command timeout error')
def step_check_command_timeout_error(context):
    """Check for command timeout error message"""
    error = context.shell_result.get("error", "")
    assert "timeout" in error.lower() or "timed out" in error.lower()


@then('the error should mention "{text}"')
def step_check_error_mentions(context, text):
    """Check if error mentions specific text"""
    error = context.shell_result.get("error", "")
    assert text in error.lower(), f"Expected '{text}' in error: {error}"


@then('I should get a safety error')
def step_check_safety_error(context):
    """Check for safety/security error"""
    error = context.shell_result.get("error", "")
    assert "dangerous" in error.lower() or "safety" in error.lower()


@then('the stdout should contain a path')
def step_check_stdout_has_path(context):
    """Check if stdout contains a path"""
    stdout = context.shell_result.get("stdout", "").strip()
    assert len(stdout) > 0
    assert "/" in stdout or "\\" in stdout  # Unix or Windows path


@then('the output should have {count:d} lines')
def step_check_line_count(context, count):
    """Check number of lines in output"""
    stdout = context.shell_result.get("stdout", "")
    lines = [l for l in stdout.split('\n') if l.strip()]
    assert len(lines) == count, f"Expected {count} lines, got {len(lines)}"


@given('there is a test directory "{directory}"')
def step_create_test_directory(context, directory):
    """Create a test directory"""
    Path(directory).mkdir(parents=True, exist_ok=True)
    context.test_dirs = getattr(context, 'test_dirs', [])
    context.test_dirs.append(directory)


def after_scenario(context, scenario):
    """Clean up test directories"""
    if hasattr(context, 'test_dirs'):
        for directory in context.test_dirs:
            if directory.startswith("/tmp/"):
                shutil.rmtree(directory, ignore_errors=True)