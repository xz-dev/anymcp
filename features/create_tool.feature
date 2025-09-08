Feature: Create new MCP tools
  As an AI assistant
  I want to create new MCP tools using Python code
  So that I can extend my capabilities dynamically

  Background:
    Given the MCP tool system is initialized
    And the tools directory is writable

  Scenario: Create a simple Python tool
    When I create a tool named "string_reverser" with the following code:
      """
      def execute(text: str) -> str:
          return text[::-1]
      """
    Then the tool should be created successfully
    And the tool file should exist in the tools directory
    And the tool should be executable

  Scenario: Create a tool with dependencies
    When I create a tool named "json_formatter" with imports:
      """
      import json
      
      def execute(data: str, indent: int = 2) -> str:
          parsed = json.loads(data)
          return json.dumps(parsed, indent=indent)
      """
    Then the tool should be created successfully
    And the tool should handle JSON formatting correctly

  Scenario: Create a tool with invalid Python syntax
    When I create a tool with invalid Python code:
      """
      def execute(
          this is not valid python
      """
    Then the tool creation should fail
    And I should get a syntax error message

  Scenario: Create a tool that already exists
    Given there is already a tool named "existing_tool"
    When I try to create a tool named "existing_tool"
    Then I should get a warning that the tool exists
    And I should be asked if I want to overwrite it

  Scenario: Create a complex tool with multiple functions
    When I create a tool named "data_analyzer" with helper functions:
      """
      def calculate_mean(numbers):
          return sum(numbers) / len(numbers)
      
      def calculate_median(numbers):
          sorted_nums = sorted(numbers)
          n = len(sorted_nums)
          if n % 2 == 0:
              return (sorted_nums[n//2-1] + sorted_nums[n//2]) / 2
          return sorted_nums[n//2]
      
      def execute(numbers: list) -> dict:
          return {
              'mean': calculate_mean(numbers),
              'median': calculate_median(numbers),
              'min': min(numbers),
              'max': max(numbers)
          }
      """
    Then the tool should be created successfully
    And the tool should calculate statistics correctly

  Scenario: Create a tool with metadata
    When I create a tool with metadata:
      """
      __tool_name__ = "Weather Fetcher"
      __description__ = "Fetches weather information"
      __version__ = "1.0.0"
      __parameters__ = {
          "city": {"type": "string", "required": True},
          "units": {"type": "string", "default": "metric"}
      }
      
      def execute(city: str, units: str = "metric") -> dict:
          return {"city": city, "temperature": 20, "units": units}
      """
    Then the tool should be created with proper metadata
    And the metadata should be searchable

  Scenario: Create a tool without execute function
    When I create a tool named "no_execute" with the following code:
      """
      def process(text: str) -> str:
          return text.upper()
      """
    Then the tool should be created successfully
    And the tool should have execute function added automatically

  Scenario: Create tool with async function
    When I create a tool named "async_tool" with the following code:
      """
      import asyncio
      
      async def execute(delay: int = 1) -> str:
          await asyncio.sleep(delay)
          return "Completed"
      """
    Then the tool should be created successfully
    And the tool should be executable

  Scenario: Create tool with error handling
    When I create a tool named "safe_divider" with the following code:
      """
      def execute(a: float, b: float) -> float:
          if b == 0:
              raise ValueError("Cannot divide by zero")
          return a / b
      """
    Then the tool should be created successfully
    And executing with b=0 should raise an error

  @skip
  Scenario: Tool name sanitization
    When I create a tool named "../../../etc/passwd" with valid code
    Then the tool creation should fail
    And I should get a security error message

  Scenario: Create tool with large code
    When I create a tool with 1000 lines of code
    Then the tool should be created successfully
    And the tool file should contain all the code