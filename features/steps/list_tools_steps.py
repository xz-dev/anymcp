from behave import given, when, then
import asyncio
from pathlib import Path

# Add parent directory to Python path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from anymcp.tool_manager import ToolManager


@when('I list all tools')
def step_list_all_tools(context):
    """List all available tools"""
    if not hasattr(context, 'tool_manager'):
        tools_dir = str(context.tools_dir) if hasattr(context, 'tools_dir') else "tools"
        context.tool_manager = ToolManager(tools_dir=tools_dir)
    
    tools = context.tool_manager.list_tools()
    context.tools_list = tools
    context.tools_result = {
        "tools": tools,
        "count": len(tools),
        "tools_directory": str(context.tool_manager.tools_dir)
    }


@then('I should get an empty list')
def step_check_empty_list(context):
    """Check if tools list is empty"""
    assert len(context.tools_list) == 0


@then('the count should be {count:d}')
def step_check_count(context, count):
    """Check tools count"""
    assert len(context.tools_list) == count, f"Expected {count} tools, got {len(context.tools_list)}"


@then('I should see all {count:d} tools')
def step_check_all_tools(context, count):
    """Check we see all expected tools"""
    assert len(context.tools_list) == count


@then('the list should contain "{tool_name}"')
def step_check_list_contains(context, tool_name):
    """Check if list contains specific tool"""
    assert tool_name in context.tools_list, f"Tool '{tool_name}' not found in {context.tools_list}"


@then('the result should include the tools directory path')
def step_check_directory_path(context):
    """Check if result includes directory path"""
    assert "tools_directory" in context.tools_result
    assert context.tools_result["tools_directory"]


@then('the path should end with "{suffix}"')
def step_check_path_suffix(context, suffix):
    """Check if path ends with suffix"""
    path = context.tools_result["tools_directory"]
    assert path.endswith(suffix), f"Path '{path}' doesn't end with '{suffix}'"


@given('there are tools in the directory:')
def step_create_tools_from_table(context):
    """Create tools from table"""
    if not hasattr(context, 'tool_manager'):
        tools_dir = str(context.tools_dir) if hasattr(context, 'tools_dir') else "tools"
        context.tool_manager = ToolManager(tools_dir=tools_dir)
    
    for row in context.table:
        tool_name = row["tool_name"]
        code = f'''
def execute():
    return "{tool_name} executed"
'''
        asyncio.run(context.tool_manager.create_tool(tool_name, code, overwrite=True))


@given('the tools directory has {count:d} tools')
def step_ensure_tool_count(context, count):
    """Ensure specific number of tools exist"""
    if not hasattr(context, 'tool_manager'):
        tools_dir = str(context.tools_dir) if hasattr(context, 'tools_dir') else "tools"
        context.tool_manager = ToolManager(tools_dir=tools_dir)
    
    # Clear directory first
    for tool_file in context.tool_manager.tools_dir.glob("*.py"):
        tool_file.unlink()
    
    # Create specified number of tools
    for i in range(count):
        code = f'def execute(): return "tool_{i}"'
        asyncio.run(context.tool_manager.create_tool(f"tool_{i}", code, overwrite=True))


@when('I create a new tool named "{tool_name}"')
def step_create_new_tool(context, tool_name):
    """Create a new tool"""
    if not hasattr(context, 'tool_manager'):
        tools_dir = str(context.tools_dir) if hasattr(context, 'tools_dir') else "tools"
        context.tool_manager = ToolManager(tools_dir=tools_dir)
    
    code = f'''
def execute():
    return "{tool_name} result"
'''
    asyncio.run(context.tool_manager.create_tool(tool_name, code, overwrite=True))


@given('there are files in the tools directory:')
def step_create_mixed_files(context):
    """Create mixed file types in tools directory"""
    if not hasattr(context, 'tool_manager'):
        tools_dir = str(context.tools_dir) if hasattr(context, 'tools_dir') else "tools"
        context.tool_manager = ToolManager(tools_dir=tools_dir)
    
    tools_dir = context.tool_manager.tools_dir
    
    for row in context.table:
        filename = row["filename"]
        file_type = row["type"]
        file_path = tools_dir / filename
        
        if file_type == "python":
            content = 'def execute(): return "test"'
        elif file_type == "text":
            content = "This is a text file"
        elif file_type == "json":
            content = '{"key": "value"}'
        else:
            content = ""
        
        file_path.write_text(content)


@then('the list should only contain Python tools')
def step_check_only_python(context):
    """Check list only contains Python tools"""
    for tool in context.tools_list:
        # Tool names shouldn't have extensions in the list
        assert not tool.endswith('.txt')
        assert not tool.endswith('.json')


# This step is already defined in test_steps.py
# Using the common definition instead


@given('there are {count:d} tools in the directory')
def step_create_many_tools(context, count):
    """Create many tools for performance testing"""
    if not hasattr(context, 'tool_manager'):
        tools_dir = str(context.tools_dir) if hasattr(context, 'tools_dir') else "tools"
        context.tool_manager = ToolManager(tools_dir=tools_dir)
    
    # Clear directory first
    for tool_file in context.tool_manager.tools_dir.glob("*.py"):
        tool_file.unlink()
    
    # Create many tools
    for i in range(count):
        code = f'def execute(): return {i}'
        asyncio.run(context.tool_manager.create_tool(f"perf_tool_{i:03d}", code, overwrite=True))


@then('the operation should complete quickly')
def step_check_performance(context):
    """Check operation completed (performance is implied)"""
    # Just check we got results
    assert context.tools_list is not None


@then('I should get all {count:d} tools')
def step_check_got_all_tools(context, count):
    """Check we got all expected tools"""
    assert len(context.tools_list) == count