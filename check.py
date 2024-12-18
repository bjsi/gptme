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
    pass

from gptme.tools.shell import execute_shell, get_shell_command, execute_shell_impl

def test_execute_shell():
    def mock_confirm(msg):
        return True

    cmd = "echo 'Hello, World!'"
    result = list(execute_shell(None, None, {"command": cmd}, mock_confirm))
    
    assert len(result) == 1
    assert result[0].role == "system"
    assert "Ran command" in result[0].content
    assert "Hello, World!" in result[0].content