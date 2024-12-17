import subprocess
from gptme.tools import ToolSpec, ToolUse

instructions = "Use this tool to search the contents of files in the codebase. This is useful for finding the definition of a class, function, or variable."


def examples(tool_format):
    return f"""
> User: search for occurrences of the `run` function in the current directory
> Assistant:
{ToolUse("ipython", [], "search('def run')").to_output(tool_format)}
> User: search for occurrences of the `run` or `save` functions in the test directory
> Assistant:
{ToolUse("ipython", [], "search('run|save', 'test')").to_output(tool_format)}
> User: search for the definition of the `Mail` class
> Assistant:
{ToolUse("ipython", [], "search('class Mail')").to_output(tool_format)}
""".strip()

def search(query: str, directory: str = "."):
    res = subprocess.run(["rga", "--line-number", "--context", "2", "--heading", "-e", query, directory], capture_output=True, text=True)
    results = res.stdout.strip()
    if not results: return "No results found."
    return f"{results}\nYou can get more context by using the `read` tool with a line_range parameter."

tool = ToolSpec(
    name="search",
    desc="Search the contents of files in the codebase",
    instructions=instructions,
    examples=examples,
    functions=[search],
)