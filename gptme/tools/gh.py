import shutil

from . import ToolSpec, ToolUse


def has_gh_tool() -> bool:
    return shutil.which("gh") is not None


instructions = "Interact with GitHub via the GitHub CLI (gh). Use the `shell` tool with the `gh` command."


def examples(tool_format):
    return f"""
> User: read the issue
> Assistant:
{ToolUse("shell", [], "gh issue view $ISSUE --comments").to_output(tool_format)}
"""


# Note: this isn't actually a tool, it only serves prompting purposes
tool: ToolSpec = ToolSpec(
    name="gh",
    available=has_gh_tool(),
    desc="Interact with GitHub",
    instructions=instructions,
    examples=examples,
)
