#!/usr/bin/env python3

import json
import subprocess
import sys
import os

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <issue>")
        sys.exit(1)
        
    issue = sys.argv[1]
    
    # Environment variables
    os.environ["ISSUE"] = issue
    os.environ["ALLOW_EDIT"] = "check.py"
    os.environ["POST_PATCH_MSG"] = "1) Please only write and run one test at a time. 2) If you need more context, use the `read` or `search` tools."
    os.environ["PATCH_REQUEST_MSG"] = "Please only write and run one test at a time."

    init_check_py = """import sys
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
"""

    with open("check.py", "w") as f:
        f.write(init_check_py)

    # User prompt
    user_prompt = """You are a code explanation checker.
- Given an explanation of the behavior of part of a codebase in `explanation.md`, your task is to check whether the explanation is correct.
- Start by setting up the `check.py` file with the necessary boilerplate to run tests using pytest.
- Then read the explanation in `explanation.md`.
- For each bullet point in the explanation, read the relevant code using the `read` and `search` tools, then write and run a unit test in `check.py` to check whether the explanation is correct.
- Correct any inaccuracies or omissions in the `explanation.md` file as you go.

When editing and running code:
- To create or edit files use the `patch` tool.
- To execute code use the `shell` tool.
- To run tests use pytest in the `shell` tool.

You will think step by step when solving a problem to plan your next action in `<planning>` tags.
After you receive feedback on the result of your action, you will reflect on the outcome in `<reflection>` tags."""

    # Assistant messages
    assistant_msg1 = """Certainly! Let's get started.
    
<planning>
1. We should start by creating the `check.py` file.
2. First let's request permission to use the `patch` tool to create the `check.py` file.
</planning>

```ipython
request_to_patch('check.py', region=(1, 1), patch_description='Initialise the check.py file')
```"""

    assistant_msg2 = f"""<reflection>
<outcome>success</outcome>
My request to create the `check.py` file was approved.
</reflection>

Thanks for approving the patch!

<planning>
1. Now let's create the `check.py` file.
2. We need to add the necessary testing boilerplate to the `check.py` file using the `patch` tool.
</planning>

```patch check.py (1, 1)
{init_check_py}
```"""

    # Create initial messages list
    init_messages = [
        {"role": "user", "content": user_prompt},
        {"role": "assistant", "content": assistant_msg1},
        {"role": "system", "content": "Approved."},
        {"role": "assistant", "content": assistant_msg2},
        {"role": "system", "content": "Approved."},
    ]

    # Run gptme command
    subprocess.run(["gptme", "-n", f"check-explanation-issue-{issue}", "--tools", "gh,search,read,ipython,patch", "--init-messages", json.dumps(init_messages)])

if __name__ == "__main__":
    main()