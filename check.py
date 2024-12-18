import unittest
import sys
import io
from contextlib import redirect_stdout
from gptme.message import Message
class TestCodeBehavior(unittest.TestCase):
    def setUp(self):
        # Set up any necessary objects or configurations
        pass

    def tearDown(self):
        # Clean up after each test
        pass

    # Test methods will be added here

if __name__ == '__main__':
    def test_execute_shell(self):
        from gptme.tools.shell import execute_shell

        # Mock the confirm function
        def mock_confirm(msg):
            return True

        # Test with a simple command
        command = "echo 'Hello, World!'"
        result = list(execute_shell(command, None, None, mock_confirm))

        # Check if the result is a list with one Message
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], Message)
        self.assertEqual(result[0].role, "system")
        self.assertIn("Ran command", result[0].content)
        self.assertIn("Hello, World!", result[0].content)

    unittest.main()