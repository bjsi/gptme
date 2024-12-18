import pytest
from unittest.mock import patch, MagicMock
from gptme.tools.shell import execute_shell, get_shell_command, execute_shell_impl

def test_execute_shell_uses_get_shell_command():
    with patch('gptme.tools.shell.get_shell_command') as mock_get_shell_command:
        mock_get_shell_command.return_value = 'echo "test"'

def test_execute_shell_uses_execute_shell_impl():
    with patch('gptme.tools.shell.execute_shell_impl') as mock_execute_shell_impl:
        mock_execute_shell_impl.return_value = iter([])

def test_execute_shell_impl_behavior():
    with patch('gptme.tools.shell.ShellSession') as mock_shell_session:
        mock_shell = MagicMock()
        mock_shell.run.return_value = (0, "test output", "")
        mock_shell_session.return_value = mock_shell

        result = list(execute_shell_impl("echo test", None, lambda _: True))

        mock_shell.run.assert_called_once_with("echo test")
        assert len(result) == 1
        assert result[0].role == "system"
        assert "test output" in result[0].content
        mock_execute_shell_impl.assert_called_once()