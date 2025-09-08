Feature: Run tests for tools
  As an AI assistant
  I want to run tests for tools
  So that I can verify they work correctly

  Background:
    Given the MCP tool system is initialized
    And the tools directory is writable

  @skip
  Scenario: Run a specific test file
    Given there is a tool named "sample_tool"
    And there are tests for "sample_tool"
    When I run the test "sample_tool"
    Then the test execution should succeed
    And I should see test output
    And I should see test statistics

  Scenario: Run tests that don't exist
    When I run the test "nonexistent_test"
    Then the test execution should fail
    And I should get an error message about test not found

  Scenario: Run all tests
    Given there are multiple test files available
    When I run the test "all"
    Then the test execution should complete
    And I should see output from multiple test files

  Scenario: Run tests with verbose output
    Given there is a tool named "verbose_test_tool"
    And there are tests for "verbose_test_tool"
    When I run the test "verbose_test_tool" with verbose mode
    Then I should see detailed test output
    And I should see step-by-step execution

  @skip
  Scenario: Run failing tests
    Given there is a tool with bugs
    And there are tests that will fail
    When I run the test for the buggy tool
    Then the test execution should fail
    And I should see which tests failed
    And I should see failure details

  @skip
  Scenario: Parse test statistics
    Given there is a tool with comprehensive tests
    When I run the test and it completes
    Then I should see scenario statistics
    And I should see step statistics
    And the statistics should be in the result

  Scenario: Run test with custom working directory
    Given there is a test in a subdirectory
    When I run the test from a different directory
    Then the test should still execute correctly
    And the working directory should be handled properly