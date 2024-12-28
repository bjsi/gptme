import os
from pathlib import Path
import json
from gptme import Message
from gptme.eval.agents.act import act
from gptme.tools.base import ToolUse
from gptme.tools.file_ctx import FileContext
from swebench.harness.constants import SWEbenchInstance

class Fix:
    allowed_tools = frozenset(["shell", "search", "read", "ipython", "patch"])
    def act(
          self,
          model: str,
          instance: SWEbenchInstance,
          repo_dir: str,
          log_dir: str,
          **kwargs
        ):
        tool_format = "xml"
        
        # User prompt
        user_prompt = """You are a bug fixer.
# TODO

You will think step by step when solving a problem to plan your next action in `<planning>` tags.
After you receive feedback on the result of your action, reflect on the result in `<outcome>` tags.
The `<outcome>` should be a one sentence reflection on whether the action was the best choice in this context and what you would do differently next time."""

        # init_messages = [
        #     Message(role="user", content=user_prompt),
        #     Message(role="assistant", content=assistant_msg1),
        #     Message(role="system", content=f"Patch applied:\n{understanding_file_ctx.stringify()}"),
        #     Message(role="assistant", content=assistant_msg2)
        # ]

        # act(
        #     tool_format=tool_format,
        #     model=model,
        #     prompt=f"Codebase context:\n{context["read_cache.json"]}",
        #     allowlist=allowlist,
        #     initial_msgs=init_messages,
        #     repo_dir=repo_dir,
        #     log_dir=log_dir,
        #     branch="fix",
        # )

