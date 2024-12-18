import sys
import io
from contextlib import redirect_stdout
import pytest

@pytest.fixture
def setup():
    # Set up any necessary objects or configurations
    pass

@pytest.fixture
def teardown():
    # Clean up after each test
    yield
    # Cleanup code here

def test_execute_shell():
    from gptme.tools.shell import execute_shell, get_shell_command
    from gptme.message import Message
    import unittest.mock

    # Mock get_shell_command
    with unittest.mock.patch('gptme.tools.shell.get_shell_command') as mock_get_shell_command:
        mock_get_shell_command.return_value = "echo 'Hello, World!'"
        
        # Mock confirm function
        mock_confirm = unittest.mock.Mock(return_value=True)
        
        # Call execute_shell
        list(execute_shell("test command", None, None, mock_confirm))
        
        # Assert that get_shell_command was called

def test_execute_shell_calls_impl():
    from gptme.tools.shell import execute_shell, execute_shell_impl
    from gptme.message import Message
    import unittest.mock

    # Mock execute_shell_impl
    with unittest.mock.patch('gptme.tools.shell.execute_shell_impl') as mock_execute_shell_impl:
        mock_execute_shell_impl.return_value = iter([Message("system", "Mocked output")])
        
        # Mock get_shell_command to return a known command
        with unittest.mock.patch('gptme.tools.shell.get_shell_command', return_value="echo 'Test'"):
            # Mock confirm function
            mock_confirm = unittest.mock.Mock(return_value=True)
            
            # Call execute_shell
            list(execute_shell("test command", None, None, mock_confirm))
            
            # Assert that execute_shell_impl was called with the correct arguments
            mock_execute_shell_impl.assert_called_once_with("echo 'Test'", None, unittest.mock.ANY)