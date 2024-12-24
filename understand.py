#!/usr/bin/env python3

import json
import subprocess
import sys
import os

from gptme.tools.base import ToolUse
from gptme.tools.file_ctx import FileContext

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <issue>")
        sys.exit(1)
        
    issue = sys.argv[1]
    
    # Environment variables
    os.environ["ISSUE"] = issue
    os.environ["ALLOW_EDIT"] = "understanding.md"
    # TODO: only show once, not repeatedly
    # os.environ["POST_PATCH_MSG"] = f"Are you sure your explanation and questions are relevant to issue {issue}?"
    os.environ["POST_PATCH_MSG"] = f"Are you sure your explanation and questions are relevant to issue {issue}? If you have checked, please continue."

    init_understanding_md = """# Current Understanding

# Questions to Investigate
"""

    # Create initial understanding.md file
    with open("understanding.md", "w") as f:
        f.write(init_understanding_md)

    understanding_file_ctx = FileContext("understanding.md")
    understanding_file_ctx.show(line_range=(1, -1))

    tool_format = "xml"

    # User prompt
    user_prompt = f"""You are a code understanding tool.
- Gather the full context required to draft a solution to the following issue: https://github.com/ErikBjare/gptme/issues/{issue}
- Keep a running log of your "Current Understanding" of the code as a nested markdown list in `understanding.md` with concise bullet points explaining the current behavior from the entrypoint to the relevant part of the codebase.
- Under that, store a running list of "Questions to Investigate". Don't add any new headings.
- Get details about the issue using `gh` and summarize it, then use `search` and `read` tools to build an understanding of the relevant parts of the codebase.
- Examine each relevant function in detail, expanding context with `read` as you go to understand the problem.
- Ignore anything that isn't relevant to issue {issue}.
- Don't make code changes - only overwrite the `understanding.md` file.

You will think step by step when solving a problem to plan your next action in `<planning>` tags.
After you receive feedback on the result of your action, reflect on the result in `<outcome>` tags.
The `<outcome>` should include a score between -1 and 1 and a one sentence reflection on whether the action was the best choice in this context and what you would do differently next time."""
    
    assistant_msg1 = f"""Certainly! Let's get started.

<planning>
1. I should create the `understanding.md` file with the `patch` tool and add the headings.
</planning>

{ToolUse("patch", ["understanding.md", "(1, 1)"], init_understanding_md).to_output(tool_format)}
"""
    assistant_msg2 = f"""<outcome><score>1.0</score>My use of the `patch` tool was correct. Based on the contents of `understanding.md` the patch was applied successfully.</outcome>

That looks correct! Now I'll start gathering context.

<planning>
1. I should start by getting details about the issue using `gh`.
2. Then I should use the `search` and `read` tools to search for relevant parts of the codebase.
</planning>

{ToolUse("shell", [], f"gh issue view {issue}").to_output(tool_format)}
"""
    
    res = subprocess.run(["gh", "issue", "view", issue], capture_output=True, text=True).stdout
    init_messages = [
        {"role": "user", "content": user_prompt},
        {"role": "assistant", "content": assistant_msg1},
        {"role": "system", "content": f"Patch applied:\n{understanding_file_ctx.stringify()}"},
        {"role": "assistant", "content": assistant_msg2},
        {"role": "system", "content": f"```stdout\n{res}\n```"},
    ]

    model = "openrouter/qwen/qwen-2.5-coder-32b-instruct"
    # model = "openrouter/meta-llama/llama-3.1-8b-instruct"

    # Run gptme command
    subprocess.run([
        "gptme", 
        "--model", model,
        "--tools", "search,read,ipython,patch,shell",
        "--tool-format", tool_format,
        "--init-messages", json.dumps(init_messages),
    ])

if __name__ == "__main__":
    main() 