import os
import subprocess
from gptme.tools import ToolSpec, ToolUse
from typing import Dict, List
from pathlib import Path

from gptme.tools.file_ctx import FileContext

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

def search_basic(query: str, directory: str = "."):
    res = subprocess.run(["rga", "--line-number", "--context", "2", "--heading", "-e", query, directory], capture_output=True, text=True)
    results = res.stdout.strip()
    if not results: return "No results found."
    return f"{results}\nYou can get more context by using the `read` tool with a line_range parameter."

def parse_search_results(results: str) -> Dict[Path, List[int]]:
    parsed: Dict[str, List[int]] = {}
    for line_num in results.splitlines():
        if not line_num.strip(): continue
        filepath, line_num, _ = line_num.split(':', 2)
        line_number = int(line_num)
        if filepath not in parsed: parsed[filepath] = []
        parsed[filepath].append(line_number)
    file_contexts: Dict[Path, FileContext] = {}
    for path, line_numbers in parsed.items():
        line_numbers.sort()
        ctx = FileContext(path)
        if path.endswith('.py'):
            ctx.show(lines=line_numbers, scope="line", parents="all")
        for line_num in line_numbers: # padding
            ctx.show_indices.add(max(line_num - 2, 0))
            ctx.show_indices.add(max(line_num - 1, 0))
            ctx.show_indices.add(line_num)
        file_contexts[path] = ctx.stringify()
    return file_contexts

def search_file_names(query: str, directory: str = "."):
    p1 = subprocess.Popen(
        ["rga", "--files", directory],
        stdout=subprocess.PIPE,
        text=True
    )
    p2 = subprocess.Popen(
        ["rga", "-e", query],
        stdin=p1.stdout,
        stdout=subprocess.PIPE,
        text=True
    )
    p1.stdout.close()
    output = p2.communicate()[0]
    return output.strip()

def search(query: str, file_or_dir: str = "."):
    """Search the contents of files in the codebase.
    Searches with rga then parses results with tree-sitter to add more context if possible.
    """
    file_contents = subprocess.run(
        ["rga", "--line-number", "--no-heading", "-e", query, file_or_dir],
        capture_output=True,
        text=True
    )
    file_names = search_file_names(query, file_or_dir)
    file_name_results = f"File name matches:\n{file_names}\n" + '-' * 80 + "\n"
    if os.path.isfile(file_or_dir):
        # If directory is a single file, prepend filename to each line
        file_contents.stdout = "\n".join(f"{file_or_dir}:{line}" for line in file_contents.stdout.splitlines())
    parsed = parse_search_results(file_contents.stdout)
    output = ""
    num_results = len(parsed.keys())
    if num_results > 40: return f"Found >{num_results} results. Please use a more specific search query."
    for path, ctx in parsed.items():
        output += f"{path}\n{ctx}\n" + '-' * 80 + "\n"
    results = output.strip()
    if not results: return "No results found."
    return f"{file_name_results}{results}\nYou can get more context by using the `read` tool with line ranges or names of functions, classes or variables."

tool = ToolSpec(
    name="search",
    desc="Search the contents of files in the codebase",
    instructions=instructions,
    examples=examples,
    functions=[search],
)