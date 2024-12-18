from gptme.message import Message
from gptme.tools.shell import execute_shell

class TestShellExecution:
    def test_execute_shell(self):
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