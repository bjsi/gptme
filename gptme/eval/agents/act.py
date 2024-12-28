import logging
from pathlib import Path
from gptme import Message
from gptme.prompts import get_prompt
from gptme.tools import init_tools
from gptme import chat as gptme_chat

logger = logging.getLogger(__name__)

def act(
    tool_format: str,
    model: str,
    prompt: str,
    allowlist: list[str] | None = None,
    initial_msgs: list[Message] | None = None,
    repo_dir: str | None = None,
    interactive: bool = True,
    log_dir: str | None = None,
    max_turns: int | None = None,
    branch: str = "main",
):
    init_tools(allowlist=allowlist)
    print("--- Start of generation ---")
    logger.debug(f"Working in {repo_dir}")
    init_prompt = [get_prompt(interactive=interactive, tool_format=tool_format)] + initial_msgs
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
            max_turns=max_turns,
            branch=branch,
        )
    except (SystemExit, KeyboardInterrupt): pass
    print("--- Finished generation ---\n")