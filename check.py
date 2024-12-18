import unittest
from unittest.mock import patch, MagicMock
from gptme.tools.shell import execute_shell

class TestShellExecution(unittest.TestCase):
    @patch('gptme.tools.shell.get_shell_command')
    @patch('gptme.tools.shell.execute_shell_impl')
    def test_execute_shell_calls_correct_functions(self, mock_execute_shell_impl, mock_get_shell_command):
        mock_get_shell_command.return_value = "test command"
        mock_execute_shell_impl.return_value = iter([])  # Assuming it returns an iterator
        
        list(execute_shell("test command"))  # Execute and consume the generator
        
        mock_get_shell_command.assert_called_once_with("test command")
        mock_execute_shell_impl.assert_called_once_with("test command")

if __name__ == '__main__':
    unittest.main()