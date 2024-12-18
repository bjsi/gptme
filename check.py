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

from unittest.mock import patch, MagicMock
from gptme.tools.shell import execute_shell, get_shell_command, execute_shell_impl

def test_execute_shell_uses_get_shell_command():
    with patch('gptme.tools.shell.get_shell_command') as mock_get_shell_command:
        mock_get_shell_command.return_value = 'echo "test"'
        list(execute_shell(None, None, None, lambda _: True))

def test_execute_shell_uses_execute_shell_impl():
    with patch('gptme.tools.shell.execute_shell_impl') as mock_execute_shell_impl, \
         patch('gptme.tools.shell.is_allowlisted', return_value=True):
        mock_execute_shell_impl.return_value = iter([])
        list(execute_shell('echo "test"', None, None, lambda _: True))
        mock_execute_shell_impl.assert_called_once()