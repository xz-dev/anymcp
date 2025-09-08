import json
import ast
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
import aiofiles
import asyncio


class ToolManager:
    def __init__(self, tools_dir: str = "tools"):
        self.tools_dir = Path(tools_dir)
        self.tools_dir.mkdir(exist_ok=True)
        
    async def search_tools(self, keyword: Optional[str] = None, detailed: bool = False) -> List[Dict[str, Any]]:
        tools = []
        
        for tool_path in self.tools_dir.glob("*.py"):
            tool_info = await self._extract_tool_info(tool_path)
            
            if keyword:
                keyword_lower = keyword.lower()
                if (keyword_lower not in tool_info["name"].lower() and 
                    keyword_lower not in tool_info.get("description", "").lower()):
                    continue
            
            if detailed:
                tools.append(tool_info)
            else:
                tools.append({
                    "name": tool_info["name"],
                    "description": tool_info.get("description", ""),
                    "path": str(tool_path)
                })
        
        return tools
    
    async def _extract_tool_info(self, tool_path: Path) -> Dict[str, Any]:
        async with aiofiles.open(tool_path, 'r') as f:
            content = await f.read()
        
        tool_info = {
            "name": tool_path.stem,
            "path": str(tool_path),
            "description": "",
            "parameters": {},
            "version": "1.0.0"
        }
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            if target.id == "__description__":
                                if isinstance(node.value, ast.Constant):
                                    tool_info["description"] = node.value.value
                            elif target.id == "__tool_name__":
                                if isinstance(node.value, ast.Constant):
                                    tool_info["name"] = node.value.value
                            elif target.id == "__version__":
                                if isinstance(node.value, ast.Constant):
                                    tool_info["version"] = node.value.value
                            elif target.id == "__parameters__":
                                try:
                                    tool_info["parameters"] = ast.literal_eval(node.value)
                                except:
                                    pass
                
                elif isinstance(node, ast.FunctionDef) and node.name == "execute":
                    params = []
                    for arg in node.args.args:
                        param_info = {"name": arg.arg}
                        if arg.annotation:
                            param_info["type"] = ast.unparse(arg.annotation)
                        params.append(param_info)
                    
                    if not tool_info["parameters"]:
                        tool_info["parameters"] = {p["name"]: p for p in params}
                    
                    if node.body and isinstance(node.body[0], ast.Expr):
                        if isinstance(node.body[0].value, ast.Constant):
                            if not tool_info["description"]:
                                tool_info["description"] = node.body[0].value.value
        except:
            pass
        
        return tool_info
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any], timeout: int = 30) -> Dict[str, Any]:
        tool_path = self.tools_dir / f"{tool_name}.py"
        
        if not tool_path.exists():
            tools = await self.search_tools(tool_name)
            if tools:
                tool_path = Path(tools[0]["path"])
            else:
                return {
                    "success": False,
                    "error": f"Tool '{tool_name}' not found"
                }
        
        params_json = json.dumps(parameters)
        
        try:
            process = await asyncio.create_subprocess_exec(
                "python", str(tool_path), params_json,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
            
            if process.returncode != 0:
                return {
                    "success": False,
                    "error": stderr.decode() if stderr else "Tool execution failed"
                }
            
            try:
                output = json.loads(stdout.decode())
                return {
                    "success": True,
                    "result": output
                }
            except json.JSONDecodeError:
                return {
                    "success": True,
                    "result": stdout.decode()
                }
                
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()  # Clean up the process
            return {
                "success": False,
                "error": f"Tool execution timed out after {timeout} seconds"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def create_tool(self, name: str, code: str, overwrite: bool = False) -> Dict[str, Any]:
        tool_path = self.tools_dir / f"{name}.py"
        
        if tool_path.exists() and not overwrite:
            return {
                "success": False,
                "error": f"Tool '{name}' already exists. Use overwrite=True to replace it."
            }
        
        try:
            ast.parse(code)
        except SyntaxError as e:
            return {
                "success": False,
                "error": f"Invalid Python syntax: {str(e)}"
            }
        
        if "def execute(" not in code:
            wrapper_code = f'''
import json
from pathlib import Path

{code}

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('params', nargs='?', default='{{}}')
    args = parser.parse_args()
    
    params = json.loads(args.params)
    result = execute(**params) if params else execute()
    
    if isinstance(result, (dict, list)):
        print(json.dumps(result))
    else:
        print(result)
'''
        else:
            if "__main__" not in code:
                code += '''

if __name__ == "__main__":
    import json
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('params', nargs='?', default='{}')
    args = parser.parse_args()
    
    params = json.loads(args.params)
    result = execute(**params) if params else execute()
    
    if isinstance(result, (dict, list)):
        print(json.dumps(result))
    else:
        print(result)
'''
        
        async with aiofiles.open(tool_path, 'w') as f:
            await f.write(wrapper_code if 'wrapper_code' in locals() else code)
        
        tool_path.chmod(0o755)
        
        return {
            "success": True,
            "message": f"Tool '{name}' created successfully",
            "path": str(tool_path)
        }
    
    async def create_tool_test(self, tool_name: str, test_scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        feature_path = Path("features") / f"test_{tool_name}.feature"
        steps_path = Path("features/steps") / f"test_{tool_name}_steps.py"
        
        feature_path.parent.mkdir(exist_ok=True)
        steps_path.parent.mkdir(exist_ok=True)
        
        feature_content = f"""Feature: Test {tool_name} tool
  Testing the {tool_name} tool functionality

  Background:
    Given the "{tool_name}" tool is available
"""
        
        for i, scenario in enumerate(test_scenarios, 1):
            feature_content += f"""
  Scenario: Test case {i}
    When I execute "{tool_name}" with parameters:
      | parameter | value |
"""
            for param, value in scenario.get("input", {}).items():
                feature_content += f"      | {param} | {value} |\n"
            
            if "expected" in scenario:
                feature_content += f"    Then the result should be \"{scenario['expected']}\"\n"
            if "error" in scenario:
                feature_content += f"    Then an error should occur with message \"{scenario['error']}\"\n"
        
        # Use a unique step function name to avoid conflicts
        steps_content = f'''from behave import given, when, then
import json
from pathlib import Path
import asyncio

# Add parent directory to Python path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from anymcp.tool_manager import ToolManager

# Use the common step definitions if they exist, otherwise define them
try:
    from common_steps import *
except ImportError:
    @given('the "{{tool_name}}" tool is available')
    def step_{tool_name}_tool_available(context, tool_name):
        context.tool_manager = ToolManager()
        context.tool_name = tool_name

    @when('I execute "{{tool_name}}" with parameters')
    def step_{tool_name}_execute_with_params(context, tool_name):
        params = {{}}
        for row in context.table:
            params[row["parameter"]] = row["value"]
        
        result = asyncio.run(context.tool_manager.execute_tool(tool_name, params))
        context.result = result

    @then('the result should be "{{expected}}"')
    def step_{tool_name}_check_result(context, expected):
        assert context.result["success"], f"Tool execution failed: {{context.result}}"
        assert str(context.result["result"]) == expected, f"Expected {{expected}}, got {{context.result['result']}}"

    @then('an error should occur with message "{{message}}"')
    def step_{tool_name}_check_error(context, message):
        assert not context.result["success"], "Expected an error but tool succeeded"
        assert message in context.result["error"], f"Expected error '{{message}}', got '{{context.result['error']}}"
'''
        
        async with aiofiles.open(feature_path, 'w') as f:
            await f.write(feature_content)
        
        async with aiofiles.open(steps_path, 'w') as f:
            await f.write(steps_content)
        
        return {
            "success": True,
            "message": f"Test created for tool '{tool_name}'",
            "feature_file": str(feature_path),
            "steps_file": str(steps_path)
        }
    
    async def test_tool(self, tool_name: str, verbose: bool = False) -> Dict[str, Any]:
        feature_file = Path("features") / f"test_{tool_name}.feature"
        
        if not feature_file.exists():
            return {
                "success": False,
                "error": f"No tests found for tool '{tool_name}'"
            }
        
        cmd = ["behave", str(feature_file)]
        if verbose:
            cmd.append("-v")
        
        try:
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            return {
                "success": result.returncode == 0,
                "output": stdout.decode(),
                "error": stderr.decode() if stderr else None,
                "passed": result.returncode == 0
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def run_test(self, test_name: str, verbose: bool = False) -> Dict[str, Any]:
        """Run a specific test file or all tests"""
        if test_name == "all":
            feature_path = Path("features")
        else:
            feature_path = Path("features") / f"{test_name}.feature"
            if not feature_path.exists():
                feature_path = Path("features") / f"test_{test_name}.feature"
            
            if not feature_path.exists():
                return {
                    "success": False,
                    "error": f"Test file not found: {test_name}"
                }
        
        cmd = ["behave", str(feature_path)]
        if verbose:
            cmd.append("-v")
        
        try:
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.tools_dir.parent
            )
            
            stdout, stderr = await result.communicate()
            
            # Parse behave output for summary
            output_text = stdout.decode()
            passed = result.returncode == 0
            
            # Extract test statistics from output
            stats = {}
            for line in output_text.split('\n'):
                if 'scenarios passed' in line or 'scenarios failed' in line:
                    stats['scenarios'] = line.strip()
                elif 'steps passed' in line or 'steps failed' in line:
                    stats['steps'] = line.strip()
            
            return {
                "success": passed,
                "output": output_text,
                "error": stderr.decode() if stderr and not passed else None,
                "passed": passed,
                "statistics": stats
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def shell_command(self, command: str, timeout: int = 30, cwd: str = None) -> Dict[str, Any]:
        """Execute a shell command safely"""
        # Basic safety checks
        dangerous_commands = ['rm -rf /', 'format', 'dd if=']
        for dangerous in dangerous_commands:
            if dangerous in command.lower():
                return {
                    "success": False,
                    "error": f"Command contains potentially dangerous operation: {dangerous}"
                }
        
        try:
            # Use shell=True for complex commands, but with caution
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=cwd or str(self.tools_dir.parent)
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
                
                return {
                    "success": process.returncode == 0,
                    "stdout": stdout.decode(),
                    "stderr": stderr.decode(),
                    "exit_code": process.returncode
                }
                
            except asyncio.TimeoutError:
                process.kill()
                return {
                    "success": False,
                    "error": f"Command timed out after {timeout} seconds"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_tools(self) -> List[str]:
        """List all available tools in the tools directory"""
        tools = []
        for tool_path in self.tools_dir.glob("*.py"):
            tools.append(tool_path.stem)
        return tools