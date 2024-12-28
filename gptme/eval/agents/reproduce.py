import os
from pathlib import Path
import re
from typing import Dict

from gptme import Message
from gptme.eval.agents.act import act
from gptme.eval.swe_extra.swe_bench_extra_data import load_top_50_easiest_task_instances
from gptme.logmanager import SWEBenchInfo
from gptme.tools.base import ToolUse
from gptme.tools.file_ctx import FileContext
from swebench.harness.constants import SWEbenchInstance

class Reproduce:
    allowed_tools = frozenset(["shell", "search", "read", "ipython", "patch"])
    def act(
        self, 
        model: str, 
        instance: SWEbenchInstance, 
        repo_dir: str, 
        log_dir: str, 
        info: SWEBenchInfo,
        **kwargs
    ):
        os.environ["DISABLE_MEMORY"] = "1"
        os.environ["ALLOW_EDIT"] = "check.py"
        os.environ["POST_PATCH_MSG"] = "1) Please only write and run one test at a time. 2) If you need more context, use the `read` or `search` tools."
        os.environ["PATCH_REQUEST_MSG"] = "Please only write and run one test at a time."

        # Initial check.py content
        init_check_py = ""
        # Create initial file context
        check_file_ctx = FileContext(content=init_check_py)
        check_file_ctx.show(line_range=(1, -1))

        tool_format = "xml"
        
        # User prompt
        user_prompt = """You are a bug reproducer.
- Given an explanation of the behavior of part of a codebase in `understanding.md`, your task is to write and run unit tests in `check.py` to reproduce the bugs explained in the issue.
- Start by setting up the `check.py` file with the necessary boilerplate to run tests using pytest.
- Read the explanation and code provided by the user.
- Write and run unit tests in `check.py` to reproduce the bugs explained in the issue.
- If you need extra context, use the `read` and `search` tools.
- Correct any inaccuracies or omissions in the `understanding.md` file as you go.

You will think step by step when solving a problem to plan your next action in `<planning>` tags.
After you receive feedback on the result of your action, reflect on the result in `<outcome>` tags.
The `<outcome>` should be a one sentence reflection on whether the action was the best choice in this context and what you would do differently next time."""

        # Assistant messages
        assistant_msg1 = f"""Certainly! Let's get started.
    
<planning>
1. We should start by creating the `check.py` file.
</planning>

{ToolUse("patch", ["check.py", "(1, 1)"], init_check_py).to_output(tool_format)}
"""
        
        assistant_msg2 = f"""<outcome><score>1.0</score>My use of the `patch` tool was correct. Based on the contents of `check.py` the patch was applied successfully.</outcome> 

Now I'll read the explanation provided by the user.

<planning>
1. I should read the explanation and codebase context provided by the user.
</planning>

{ToolUse("ipython", [], 'read("understanding.md")').to_output(tool_format)}
"""
        
        understanding_content = info.artifacts["understanding.md"]
        lines = understanding_content.split("\n")
        idx = -1
        for i, line in enumerate(lines):
            if re.match(r"^#.*question", line, re.IGNORECASE):
                idx = i
                break
        understanding_content = "\n".join(lines[:idx])
        understanding_file_ctx = FileContext(content=understanding_content)
        understanding_file_ctx.show(line_range=(1, -1))
        system_msg = f"""{understanding_file_ctx.stringify()}"""

        # Create initial messages list
        init_messages = [
            Message(role="user", content=user_prompt),
            Message(role="assistant", content=assistant_msg1),
            Message(role="system", content=f"Patch applied:\n{check_file_ctx.stringify()}"),
            Message(role="assistant", content=assistant_msg2),
            Message(role="system", content=system_msg),
        ]

        # Tools
        codebase_context = ""
        for file, content in info.artifacts["read_cache.json"].items():
            codebase_context += f"{file}:\n{content}\n" + "---" * 10 + "\n"

        act(
            tool_format=tool_format,
            model=model,
            prompt=f"Codebase context:\n{codebase_context}\n\nWrite and run one unit test at a time.",
            allowlist=self.allowed_tools,
            initial_msgs=init_messages,
            repo_dir=repo_dir,
            log_dir=log_dir,
            branch="reproduce",
        )

        files = {}
        check_file = Path(repo_dir) / "check.py"
        with open(check_file) as f: files["check.py"] = f.read()
        info.artifacts.update(files)
        info.save_to_log_dir(log_dir)
