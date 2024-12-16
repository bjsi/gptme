import subprocess
from gptme.tools import ToolSpec, ToolUse

instructions = "Use this tool to search the contents of files in the codebase. You can specify a directory to search in, otherwise the current directory is used."


def examples(tool_format):
    return f"""
> User: search for occurrences of 'document' in the current directory
> Assistant:
{ToolUse("ipython", [], "search('document')").to_output(tool_format)}
> User: search for occurrences of 'run' or 'save' in the test directory
> Assistant:
{ToolUse("ipython", [], "search('run|save', 'test')").to_output(tool_format)}
""".strip()

def search(query: str, directory: str = "."):
    res = subprocess.run(["rga", "--line-number", "--context", "2", "--heading", "-e", query, directory], capture_output=True, text=True)
    return res.stdout

tool = ToolSpec(
    name="search",
    desc="Search the contents of files in the codebase",
    instructions=instructions,
    examples=examples,
    functions=[search],
)