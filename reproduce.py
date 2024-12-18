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
    os.environ["ALLOW_EDIT"] = "understanding.md,check.py"
    os.environ["POST_PATCH_MSG"] = "1) Please only write and run one test at a time. 2) If you need more context, use the `read` or `search` tools."
    os.environ["PATCH_REQUEST_MSG"] = "Please only write and run one test at a time."

    # Initial content templates
    init_understanding = """# Current understanding

# Questions to investigate
"""

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

    # Write initial files
    with open("understanding.md", "w") as f:
        f.write(init_understanding)
    
    with open("check.py", "w") as f:
        f.write(init_check_py)

    # User prompt
    user_prompt = """You are a code explanation checker.
- Given an explanation of the behavior of part of a codebase in `explanation.md`, your task is to check whether the explanation is correct.
- Start by reading the explanation in `explanation.md`.
- For each bullet point in the explanation, you should read the relevant code using the `read` and `search` tools. Then, write and run a unit test in `check.py` to check whether the explanation is correct.
- Don't change the codebase, only write and run tests to check the explanation.

When editing and running code:
- To create or edit files use the `patch` tool.
- To execute code use the `shell` tool.
- To run tests use pytest in the `shell` tool.

Use `<thinking>` tags to think before you answer."""

    # Assistant messages
    assistant_msg1 = """Certainly! Let's start by creating the `understanding.md` and `check.py` files.

<thinking>
1. First, let's do a patch to create the `understanding.md` file and add the requested headings.
2. Then, we'll do a patch to create the `check.py` file and add the necessary testing boilerplate.
3. We'll use the `read` and `search` tools to examine the relevant functions and tests in detail.
4. As we go, we'll keep a log of our understanding in `understanding.md`.
5. We'll also maintain a list of questions to investigate further.
</thinking>

Let's begin by creating the `understanding.md` file:

```ipython
request_to_patch('understanding.md', region=(1, 1), patch_description='Initialise the understanding.md file')
```"""

    assistant_msg2 = f"""Thank you for approving the creation of the new file. Now, let's apply the patch to create the `understanding.md` file with the desired headings:

```patch understanding.md (1, 1)
{init_understanding}
```"""

    assistant_msg3 = """Thank you. Now, let's create the `check.py` file:

```ipython
request_to_patch('check.py', region=(1, 1), patch_description='Initialise the check.py file')
```"""

    assistant_msg4 = f"""Thank you. Now, let's apply the patch to create the `check.py` file:

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
        {"role": "assistant", "content": assistant_msg3},
        {"role": "system", "content": "Approved."},
        {"role": "assistant", "content": assistant_msg4},
        {"role": "system", "content": "Approved."}
    ]

    print(json.dumps(init_messages))

    # Run gptme command
    # cmd = f'gptme -n "check-explanation-issue-{issue}" --tools gh,search,read,ipython,patch --init-messages \'{json.dumps(init_messages)}\' "Great, let\'s continue."'
    subprocess.run(["gptme", "-n", f"check-explanation-issue-{issue}", "--tools", "gh,search,read,ipython,patch", "--init-messages", json.dumps(init_messages)])

if __name__ == "__main__":
    main()