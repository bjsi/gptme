#!/usr/bin/env python3

import json
import subprocess
import sys
import os

from gptme.tools.file_ctx import FileContext

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <issue>")
        sys.exit(1)
        
    issue = sys.argv[1]
    
    # Environment variables
    os.environ["ISSUE"] = issue
    os.environ["ALLOW_EDIT"] = "understanding.md"
    os.environ["POST_PATCH_MSG"] = f"Are you sure your explanation and questions are relevant to issue {issue}?"
    os.environ["REQUEST_TO_PATCH"] = "1"

    init_understanding_md = """# Current Understanding

# Questions to Investigate
"""

    # Create initial understanding.md file
    with open("understanding.md", "w") as f:
        f.write(init_understanding_md)

    # User prompt
    user_prompt = f"""You are a code understanding tool.
- Gather the full context required to draft a solution to the following issue: https://github.com/ErikBjare/gptme/issues/{issue}
- Keep a running log of your "Current Understanding" of the code as a nested markdown list in `understanding.md` with concise bullet points explaining the current behavior from the entrypoint to the relevant part of the codebase.
- Under that, store a running list of "Questions to Investigate".
- Get details about the issue using `gh`, and use `search` and `read` tools to build an understanding of the relevant parts of the codebase.
- Examine each relevant function in detail, expanding context with `read` as you go to understand the problem.
- Ignore anything that isn't relevant to issue {issue}.
- Don't make code changes - only overwrite the `understanding.md` file.
- You will think step by step when solving a problem to plan your next action in `<planning>` tags.
- After you receive feedback on the result of your action, you will reflect on the outcome in `<reflection>` tags.
"""

    assistant_msg1 = f"""Certainly! Let's get started.

<planning>
1. I should start by creating the `understanding.md` file and adding the initial headings.
2. Let's begin by requesting permission to create the `understanding.md` file.
</planning>

```ipython
request_to_patch('understanding.md', region=(1, 1), patch_description='Initialise the understanding.md file')
```"""
    
    assistant_msg2 = f"""Thanks for approving the patch!

<reflection>
<outcome>success</outcome>
My request to create the `understanding.md` file was approved.
</reflection>

<planning>
1. Next we should add the initial headings to the `understanding.md` file.
</planning>

```patch understanding.md (1, 1)
{init_understanding_md}
```"""
    
    understanding_file_ctx = FileContext("understanding.md")
    understanding_file_ctx.show(line_range=(1, -1))

    # Create initial messages list
    init_messages = [
        {"role": "user", "content": user_prompt},
        {"role": "assistant", "content": assistant_msg1},
        {"role": "system", "content": "Approved."},
        {"role": "assistant", "content": assistant_msg2},
        {"role": "system", "content": f"Patch applied:\n{understanding_file_ctx.stringify()}"},
    ]

    # Run gptme command
    subprocess.run([
        "gptme", 
        "-n", f"understand-issue-{issue}", 
        "--tools", "gh,search,read,ipython,patch",
        "--init-messages", json.dumps(init_messages)
    ])

if __name__ == "__main__":
    main() 