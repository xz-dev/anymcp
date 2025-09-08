Feature: Create BDD tests for MCP tools
  As an AI assistant
  I want to create BDD tests for MCP tools using behave
  So that I can ensure tools work correctly before using them

  Background:
    Given the MCP tool system is initialized
    And behave is installed and configured

  Scenario: Create a basic test for a simple tool
    Given there is a tool named "string_reverser"
    When I create a BDD test for the tool with test cases:
      | input    | expected |
      | hello    | olleh    |
      | world    | dlrow    |
      | ""       | ""       |
    Then the test file should be created in features directory
    And the test should follow behave format
    And the test should be runnable

  Scenario: Create tests with multiple scenarios
    Given there is a tool named "calculator"
    When I create BDD tests with multiple scenarios:
      """
      Scenario: Addition
        When I add 5 and 3
        Then the result should be 8
      
      Scenario: Subtraction  
        When I subtract 3 from 10
        Then the result should be 7
      
      Scenario: Division by zero
        When I divide 10 by 0
        Then an error should be raised
      """
    Then all scenarios should be included in the test file
    And each scenario should have proper step definitions

  Scenario: Create tests with complex data tables
    Given there is a tool named "data_processor"
    When I create tests with data tables:
      """
      Scenario Outline: Process various data types
        When I process <input_type> data: <input>
        Then the output should be <output>
        And the format should be <format>
        
        Examples:
          | input_type | input      | output     | format |
          | json       | {"a": 1}   | {"a": 1}   | json   |
          | csv        | a,b\\n1,2   | [["a","b"]] | list  |
          | text       | hello      | HELLO      | string |
      """
    Then the test should handle all data variations
    And the step definitions should parse the table correctly

  Scenario: Create tests with background setup
    When I create a test with background setup:
      """
      Background:
        Given the database is initialized
        And test data is loaded
        And the tool is configured with test settings
      
      Scenario: Process with test data
        When I execute the tool
        Then it should use the test data
        And the results should be reproducible
      """
    Then the background steps should run before each scenario
    And the test should have proper setup and teardown

  Scenario: Generate step definitions automatically
    Given there is a tool named "file_handler"
    When I create a test without step definitions
    Then step definition stubs should be generated
    And the stubs should match the test scenarios
    And the stubs should include parameter hints

  Scenario: Create tests with async operations
    Given there is an async tool named "async_fetcher"
    When I create tests for async operations:
      """
      Scenario: Fetch data asynchronously
        When I fetch data from multiple sources concurrently
        Then all requests should complete
        And the results should be aggregated correctly
      """
    Then the test should handle async/await properly
    And the test should use appropriate async test runners