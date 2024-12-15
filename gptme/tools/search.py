from . import ToolSpec, ToolUse

instructions = (
    "Search the contents of files using the `rga` command with the `shell` tool. Always use the `--line-number`, `--heading` and `--context 2`. You can retrieve more details from search results using the `read` tool."
)


def examples(tool_format):
    return f"""
> User: search for occurrences of 'document' in the current directory
> Assistant:
{ToolUse("shell", [], "rga --line-number --context 2 --heading -e 'document' .").to_output(tool_format)}
""".strip()


# Note: this isn't actually a tool, it only serves prompting purposes
tool = ToolSpec(
    name="search",
    desc="Search the contents of files",
    instructions=instructions,
    examples=examples,
)