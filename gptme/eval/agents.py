import logging
from abc import abstractmethod
import os
from pathlib import Path
from gptme import Message
from gptme import chat as gptme_chat
from gptme import get_prompt
from gptme.cli import get_name
from gptme.dirs import get_logs_dir
from gptme.eval.swe_extra.swe_bench_test_spec import instance_to_trajectory_info
from gptme.tools import init_tools
from gptme.tools.base import ToolUse
from gptme.tools.file_ctx import FileContext
from swebench.harness.constants import SWEbenchInstance

from .filestore import FileStore
from .types import Files

logger = logging.getLogger(__name__)


class Agent:
    def __init__(self, model: str):
        self.model = model

    @abstractmethod
    def act(self, prompt: str) -> Files:
        """
        Carries out the prompt and returns artifacts in the form of `Files`.
        """
        raise NotImplementedError


class GPTMe(Agent):
    def act(
        self,
        tool_format: str,
        model: str,
        prompt: str,
        allowlist: list[str] | None = None,
        initial_msgs: list[Message] | None = None,
        repo_dir: str | None = None,
        interactive: bool = True,
        **kwargs,
    ):
        _id = abs(hash(prompt)) % 1000000
        name = get_name(f"gptme-evals-{model.replace('/', '--')}-{_id}")
        log_dir = get_logs_dir() / name

        store = FileStore(working_dir=Path(repo_dir))

        init_tools(allowlist=allowlist)

        print("\n--- Start of generation ---")
        logger.debug(f"Working in {store.working_dir}")
        prompt_system = get_prompt(interactive=interactive, tool_format=tool_format)
        init_prompt = [prompt_system] + initial_msgs
        try:
            gptme_chat(
                tool_format=tool_format,
                prompt_msgs=[Message("user", prompt)],
                initial_msgs=init_prompt,
                logdir=log_dir,
                model=model,
                no_confirm=(not interactive),
                interactive=interactive,
                workspace=Path(repo_dir),
                **kwargs,
            )
        # don't exit on sys.exit()
        except (SystemExit, KeyboardInterrupt):
            pass
        print("--- Finished generation ---\n")

        return store.download()


class UnderstandAgent:
    def act(self, model: str, instance: SWEbenchInstance, repo_dir: str) -> Files:
        agent = GPTMe(model=model)
        # Environment variables
        os.environ["ALLOW_EDIT"] = "understanding.md"
        os.environ["POST_PATCH_MSG"] = f"Are you sure your explanation and questions are relevant to the issue? If you have checked, please continue."
        # Tools
        allowlist = frozenset(["shell", "search", "read", "ipython", "patch"])

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
""" # TODO
        
        init_messages = [
            Message(role="user", content=user_prompt),
            Message(role="assistant", content=assistant_msg1),
            Message(role="system", content=f"Patch applied:\n{understanding_file_ctx.stringify()}"),
            Message(role="assistant", content=assistant_msg2)
        ]
        return agent.act(tool_format=tool_format, model=model, prompt=f"```stdout\n{instance['problem_statement']}\n```", allowlist=allowlist, initial_msgs=init_messages, repo_dir=repo_dir, swe_bench_info=instance_to_trajectory_info(instance, model))
