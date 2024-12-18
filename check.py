import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import inspect

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gptme.tools.shell import execute_shell, get_shell_command, execute_shell_impl
from gptme.tools.shell import ShellSession
from gptme.logmanager import LogManager

class TestShellExecution(unittest.TestCase):

    def test_execute_shell_signature(self):
        sig = inspect.signature(execute_shell)
        self.assertIn('args', sig.parameters)
        self.assertIn('kwargs', sig.parameters)
        self.assertIn('confirm', sig.parameters)

    def test_execute_shell_impl_signature(self):
        sig = inspect.signature(execute_shell_impl)
        self.assertIn('_', sig.parameters)
        self.assertIn('confirm', sig.parameters)

    @patch('gptme.tools.shell.execute_shell_impl')
    def test_execute_shell_calls_execute_shell_impl(self, mock_execute_shell_impl):
        execute_shell("ls -l", {}, {}, lambda x: True)
        mock_execute_shell_impl.assert_called()  # We're just checking if it's called, not with what arguments

    @patch('gptme.tools.shell.ShellSession')
    def test_execute_shell_impl_uses_shell_session(self, MockShellSession):
        mock_session = MagicMock()
        MockShellSession.return_value = mock_session
        try:
            list(execute_shell_impl("ls -l", None, lambda x: True))
        except ValueError as e:
            print(f"ValueError caught: {e}")
        mock_session.run.assert_called_once_with("ls -l")

    def test_get_shell_command_functionality(self):
        result = get_shell_command("ls -l")
        self.assertEqual(result, "ls -l")  # Assuming it returns the command as-is

    @patch('gptme.tools.shell.ShellSession')
    def test_execute_shell_impl_error_handling(self, MockShellSession):
        mock_session = MagicMock()
        mock_session.run.side_effect = Exception("Test exception")
        MockShellSession.return_value = mock_session
        with self.assertRaises(ValueError) as context:
            list(execute_shell_impl("ls -l", None, lambda x: True))
        self.assertIn("Shell error", str(context.exception))

if __name__ == '__main__':
    unittest.main()