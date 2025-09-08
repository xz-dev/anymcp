#!/usr/bin/env python3
"""
AnyMCP 使用示例
演示如何使用 AnyMCP 创建、测试和执行工具
"""

import asyncio
import json
from anymcp.tool_manager import ToolManager


async def main():
    print("=== AnyMCP 使用示例 ===\n")
    
    # 初始化工具管理器
    tool_manager = ToolManager()
    
    # 1. 搜索现有工具
    print("1. 搜索现有工具:")
    tools = await tool_manager.search_tools()
    print(f"   找到 {len(tools)} 个工具")
    for tool in tools:
        print(f"   - {tool['name']}: {tool['description']}")
    print()
    
    # 2. 创建新工具
    print("2. 创建新工具 'word_counter':")
    code = '''
__tool_name__ = "Word Counter"
__description__ = "Counts words, characters and lines in text"
__version__ = "1.0.0"

def execute(text: str) -> dict:
    """Count words, characters and lines in text"""
    lines = text.split('\\n')
    words = text.split()
    
    return {
        "lines": len(lines),
        "words": len(words),
        "characters": len(text),
        "characters_no_spaces": len(text.replace(' ', '').replace('\\n', ''))
    }
'''
    
    result = await tool_manager.create_tool("word_counter", code, overwrite=True)
    print(f"   {result['message']}")
    print()
    
    # 3. 执行工具
    print("3. 执行 word_counter 工具:")
    test_text = "Hello World!\\nThis is a test.\\nThree lines here."
    exec_result = await tool_manager.execute_tool(
        "word_counter",
        {"text": test_text}
    )
    if exec_result["success"]:
        print(f"   输入文本: {repr(test_text)}")
        print(f"   结果: {json.dumps(exec_result['result'], indent=2)}")
    print()
    
    # 4. 创建工具测试
    print("4. 为 word_counter 创建测试:")
    test_scenarios = [
        {
            "input": {"text": "Hello World"},
            "expected": '{"lines": 1, "words": 2, "characters": 11, "characters_no_spaces": 10}'
        },
        {
            "input": {"text": "One\\nTwo\\nThree"},
            "expected": '{"lines": 3, "words": 3, "characters": 13, "characters_no_spaces": 11}'
        },
        {
            "input": {"text": ""},
            "expected": '{"lines": 1, "words": 0, "characters": 0, "characters_no_spaces": 0}'
        }
    ]
    
    test_result = await tool_manager.create_tool_test("word_counter", test_scenarios)
    print(f"   {test_result['message']}")
    print(f"   测试文件: {test_result['feature_file']}")
    print()
    
    # 5. 执行另一个工具示例 - Calculator
    if any(t['name'] == 'calculator' or t['name'] == 'example_calculator' for t in tools):
        print("5. 执行 Calculator 工具:")
        calc_result = await tool_manager.execute_tool(
            "example_calculator",
            {"operation": "multiply", "a": 7, "b": 6}
        )
        if calc_result["success"]:
            print(f"   7 × 6 = {calc_result['result']}")
        else:
            print(f"   错误: {calc_result['error']}")
        print()
    
    # 6. 搜索特定工具
    print("6. 搜索包含 'text' 的工具:")
    text_tools = await tool_manager.search_tools(keyword="text")
    for tool in text_tools:
        print(f"   - {tool['name']}: {tool['description']}")
    print()
    
    # 7. 获取工具详细信息
    print("7. 获取工具详细信息:")
    detailed_tools = await tool_manager.search_tools(detailed=True)
    if detailed_tools:
        tool = detailed_tools[0]
        print(f"   工具: {tool['name']}")
        print(f"   版本: {tool.get('version', 'N/A')}")
        print(f"   描述: {tool.get('description', 'N/A')}")
        print(f"   参数: {json.dumps(tool.get('parameters', {}), indent=2)}")
    
    print("\n=== 示例完成 ===")


if __name__ == "__main__":
    asyncio.run(main())