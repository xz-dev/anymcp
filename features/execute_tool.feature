Feature: Execute MCP tools
  As an AI assistant
  I want to execute MCP tools with parameters
  So that I can use their functionality

  Background:
    Given the MCP tool system is initialized
    And there is a sample calculator tool available

  Scenario: Execute a simple tool with parameters
    When I execute the "calculator" tool with operation "add" and numbers 5 and 3
    Then the tool should execute successfully
    And the result should be 8

  Scenario: Execute a tool without required parameters
    When I execute the "calculator" tool without parameters
    Then the execution should fail
    And I should get an error message about missing parameters

  Scenario: Execute a non-existent tool
    When I execute a tool named "non_existent_tool"
    Then the execution should fail
    And I should get an error message that the tool was not found

  Scenario: Execute a tool that returns structured data
    Given there is a "data_processor" tool available
    When I execute the tool with valid JSON input
    Then the tool should return structured JSON output
    And the output should be parseable

  Scenario: Execute a tool with file output
    Given there is a "file_generator" tool available
    When I execute the tool to generate a file
    Then the tool should create the specified file
    And the file should contain the expected content

  Scenario: Handle tool execution timeout
    Given there is a "slow_tool" that takes long to execute
    When I execute the tool with a timeout of 1 seconds
    And the tool takes longer than 1 seconds
    Then the execution should be terminated
    And I should get a timeout error message