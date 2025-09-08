Feature: Execute shell commands
  As an AI assistant
  I want to execute shell commands
  So that I can interact with the system and gather information

  Background:
    Given the MCP tool system is initialized

  Scenario: Execute a simple command
    When I execute the shell command "echo 'Hello World'"
    Then the command should execute successfully
    And the stdout should contain "Hello World"
    And the exit code should be 0

  Scenario: Execute a command with error
    When I execute the shell command "ls /nonexistent/directory"
    Then the command should fail
    And the stderr should contain error message
    And the exit code should not be 0

  Scenario: Execute command with timeout
    When I execute the shell command "sleep 5" with timeout 1 seconds
    Then the command should timeout
    And I should get a command timeout error

  Scenario: Block dangerous commands
    When I execute the shell command "rm -rf /"
    Then the command should be blocked
    And I should get a safety error
    And the error should mention "dangerous operation"

  Scenario: Execute command in custom directory
    Given there is a test directory "/tmp/test_dir"
    When I execute "pwd" in the directory "/tmp/test_dir"
    Then the command should execute successfully
    And the stdout should contain "/tmp/test_dir"

  Scenario: Execute pipe commands
    When I execute the shell command "echo -e 'line1\nline2\nline3' | grep line2"
    Then the command should execute successfully
    And the stdout should contain "line2"
    And the stdout should not contain "line1"

  Scenario: Execute command with environment variables
    When I execute the shell command "echo $HOME"
    Then the command should execute successfully
    And the stdout should contain a path

  Scenario: Execute multiple commands
    When I execute the shell command "echo 'first' && echo 'second'"
    Then the command should execute successfully
    And the stdout should contain "first"
    And the stdout should contain "second"

  Scenario: Handle command not found
    When I execute the shell command "nonexistentcommand123"
    Then the command should fail
    And the stderr should contain "not found" or "No such file"

  Scenario: Execute command with arguments
    When I execute the shell command "python -c 'print(2+2)'"
    Then the command should execute successfully
    And the stdout should contain "4"

  Scenario: Capture large output
    When I execute the shell command "for i in {1..100}; do echo $i; done"
    Then the command should execute successfully
    And the stdout should contain "1"
    And the stdout should contain "100"
    And the output should have 100 lines