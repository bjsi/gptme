import unittest
import sys
import io
from contextlib import redirect_stdout
from gptme.message import Message
class TestShellExecution:
    def test_execute_shell(self):
        from gptme.tools.shell import execute_shell

        # Mock the confirm function
        def mock_confirm(msg):
            return True

        # Test with a simple command
        command = "echo 'Hello, World!'"
        result = list(execute_shell(command, None, None, mock_confirm))

        # Check if the result is a list with one Message
        assert len(result) == 1
        assert isinstance(result[0], Message)
        assert result[0].role == "system"
        assert "Ran command" in result[0].content
        assert "Hello, World!" in result[0].content