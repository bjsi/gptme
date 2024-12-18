import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gptme.tools.shell import execute_shell, get_shell_command, execute_shell_impl
from gptme.tools.shell import ShellSession
from gptme.logmanager import LogManager

class TestShellExecution(unittest.TestCase):

    def test_execute_shell_calls_get_shell_command(self):
        with patch('gptme.tools.shell.get_shell_command') as mock_get_shell_command:
            with patch('gptme.tools.shell.execute_shell_impl') as mock_execute_shell_impl:
                execute_shell("ls -l", {}, {}, lambda x: True)
                mock_get_shell_command.assert_called_once_with("ls -l")

    def test_execute_shell_calls_execute_shell_impl(self):
        with patch('gptme.tools.shell.get_shell_command') as mock_get_shell_command:
            mock_get_shell_command.return_value = "ls -l"
            with patch('gptme.tools.shell.execute_shell_impl') as mock_execute_shell_impl:
                execute_shell("ls -l", {}, {}, lambda x: True)
                mock_execute_shell_impl.assert_called_once_with("ls -l", lambda x: True)

    def test_execute_shell_impl_uses_shell_session(self):
        with patch('gptme.tools.shell.ShellSession') as MockShellSession:
            mock_session = MagicMock()
            MockShellSession.return_value = mock_session
            list(execute_shell_impl("ls -l", None, lambda x: True))
            mock_session.run.assert_called_once_with("ls -l")

    def test_execute_shell_impl_yields_system_message(self):
        with patch('gptme.tools.shell.ShellSession') as MockShellSession:
            mock_session = MagicMock()
            mock_session.run.return_value = ("output", "error")
            MockShellSession.return_value = mock_session
            result = list(execute_shell_impl("ls -l", None, lambda x: True))
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]['role'], 'system')
            self.assertIn('output', result[0]['content'])
            self.assertIn('error', result[0]['content'])

if __name__ == '__main__':
    unittest.main()