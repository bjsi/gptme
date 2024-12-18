import sys
import io
from contextlib import redirect_stdout
import pytest
from unittest.mock import patch, MagicMock

@pytest.fixture
def setup():
    # Set up any necessary objects or configurations
    pass

@pytest.fixture
def teardown():
    # Clean up after each test
    yield
    # Cleanup code here
    pass

@patch('gptme.tools.shell.get_shell_command')
def test_execute_shell_uses_get_shell_command(mock_get_shell_command):
    mock_get_shell_command.return_value = "echo 'Test'"
    
    def mock_confirm(msg):
        return True

    list(execute_shell("original command", None, None, mock_confirm))
    
    mock_get_shell_command.assert_called_once_with("original command", None, None)
from gptme.tools.shell import execute_shell, get_shell_command, execute_shell_impl

def test_execute_shell():
    def mock_confirm(msg):
        return True

    cmd = "echo 'Hello, World!'"
    result = list(execute_shell(cmd, None, None, mock_confirm))
    
    assert len(result) == 1
    assert result[0].role == "system"
    assert "Ran command" in result[0].content
    assert "Hello, World!" in result[0].content