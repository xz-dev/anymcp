Feature: List available tools
  As an AI assistant
  I want to list all available tools
  So that I know what tools I can use

  Background:
    Given the MCP tool system is initialized

  Scenario: List tools in empty directory
    Given the tools directory is empty
    When I list all tools
    Then I should get an empty list
    And the count should be 0

  Scenario: List tools with some tools present
    Given there are tools in the directory:
      | tool_name     |
      | calculator    |
      | text_processor|
      | file_handler  |
    When I list all tools
    Then I should see all 3 tools
    And the list should contain "calculator"
    And the list should contain "text_processor"
    And the list should contain "file_handler"

  Scenario: List tools returns correct directory
    When I list all tools
    Then the result should include the tools directory path
    And the path should end with "tools"

  Scenario: List tools after creating a new tool
    Given the tools directory has 2 tools
    When I create a new tool named "new_tool"
    And I list all tools
    Then the count should be 3
    And the list should contain "new_tool"

  Scenario: List tools ignores non-Python files
    Given there are files in the tools directory:
      | filename       | type   |
      | tool1.py      | python |
      | tool2.py      | python |
      | readme.txt    | text   |
      | config.json   | json   |
    When I list all tools
    Then the count should be 2
    And the list should only contain Python tools

  Scenario: List tools with special characters in names
    Given there is a tool named "my-special_tool123"
    When I list all tools
    Then the list should contain "my-special_tool123"

  Scenario: Verify list tools performance
    Given there are 50 tools in the directory
    When I list all tools
    Then the operation should complete quickly
    And I should get all 50 tools