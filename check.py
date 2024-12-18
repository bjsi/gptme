import pytest
from unittest.mock import patch, MagicMock
from gptme.tools.shell import execute_shell, get_shell_command, execute_shell_impl

def test_execute_shell_uses_get_shell_command():
    with patch('gptme.tools.shell.get_shell_command') as mock_get_shell_command:
        mock_get_shell_command.return_value = 'echo "test"'
        list(execute_shell('echo "test"', None, None, lambda _: True))
        mock_get_shell_command.assert_called_once_with('echo "test"', None, None)
