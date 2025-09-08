Feature: Search for available MCP tools
  As an AI assistant
  I want to search for available MCP tools
  So that I can discover what tools I can use

  Background:
    Given the MCP tool system is initialized
    And there are example tools in the tools directory

  Scenario: Search for all available tools
    When I search for tools without any filter
    Then I should see a list of all available tools
    And each tool should have a name and description

  Scenario: Search for tools by keyword
    When I search for tools with keyword "calc"
    Then I should only see tools that match the keyword
    And the results should include matching tool names or descriptions

  Scenario: Search in empty tools directory
    Given the tools directory is empty
    When I search for tools
    Then I should get an empty result
    And I should receive a message that no tools are available

  Scenario: Search for tools with metadata
    When I search for tools with detailed information
    Then I should see tool names
    And I should see tool descriptions
    And I should see tool parameters
    And I should see tool file paths