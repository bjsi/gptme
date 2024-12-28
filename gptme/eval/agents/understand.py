import os
from pathlib import Path
import json

from gptme import Message
from gptme.eval.agents.act import act
from gptme.tools.base import ToolUse
from gptme.tools.file_ctx import FileContext
from gptme.tools.read import save_file_read_cache
from swebench.harness.constants import SWEbenchInstance

class Understand:
    allowed_tools = frozenset(["shell", "search", "read", "ipython", "patch"])

    def act(
        self, 
        model: str, 
        instance: SWEbenchInstance, 
        repo_dir: str, 
        log_dir: str, 
        max_turns: int | None = None,
        interactive: bool = False,
        **kwargs
    ):
        # Environment variables
        os.environ["ALLOW_EDIT"] = "understanding.md"
        os.environ["POST_PATCH_MSG"] = f"Are you sure your explanation and questions are relevant to the issue? If you have checked, please continue."
        # Tools

        init_understanding_md = """# Current Understanding

# Questions to Investigate
"""

        understanding_file_ctx = FileContext(content=init_understanding_md)
        understanding_file_ctx.show(line_range=(1, -1))

        tool_format = "xml"

        # User prompt
        user_prompt = f"""You are a code understanding tool.
- Gather the full context required to draft a solution to the issue.
- Keep a running log of your "Current Understanding" of the code as a nested markdown list in `understanding.md` with concise bullet points explaining the current behavior from the entrypoint to the relevant part of the codebase.
- Under that, store a running list of "Questions to Investigate". Don't add any new headings.
- Get details about the issue using `gh` and summarize it, then use `search` and `read` tools to build an understanding of the relevant parts of the codebase.
- Examine each relevant function in detail, expanding context with `read` as you go to understand the problem.
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

{ToolUse("shell", [], f"gh issue view 100").to_output(tool_format)}
"""
        
        init_messages = [
            Message(role="user", content=user_prompt),
            Message(role="assistant", content=assistant_msg1),
            Message(role="system", content=f"Patch applied:\n{understanding_file_ctx.stringify()}"),
            Message(role="assistant", content=assistant_msg2)
        ]
        act(
            tool_format=tool_format,
            model=model,
            prompt=f"```stdout\n{instance['problem_statement']}\n```",
            allowlist=self.allowed_tools,
            initial_msgs=init_messages,
            repo_dir=repo_dir,
            log_dir=log_dir,
            max_turns=max_turns,
            branch="understand",
            interactive=interactive,
        )
        files = {}
        understanding_file = Path(repo_dir) / "understanding.md"
        with open(understanding_file) as f: files["understanding.md"] = f.read()
        save_file_read_cache(ignore_files=["understanding.md", "read_cache.json"])
        read_file_json = Path(repo_dir) / "read_cache.json"
        with open(read_file_json, "r") as f: files.update({"read_cache.json": json.load(f)})
        return files