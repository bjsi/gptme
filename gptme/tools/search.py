import subprocess
from gptme.tools import ToolSpec, ToolUse
from typing import Dict, List
from pathlib import Path

from gptme.tools.file_ctx import FileContext

instructions = "Use this tool to search the contents of files in the codebase."

hidden_files = ["check.py", "understanding.md", "read_cache.json"]

def examples(tool_format):
    return f"""
> User: find the `run` function.
> Assistant:
{ToolUse("ipython", [], "search(query='def run')").to_output(tool_format)}

> User: find the `run` or `save` functions.
> Assistant:
{ToolUse("ipython", [], "search(query='def run|def save')").to_output(tool_format)}

> User: find the `Mail` class
> Assistant:
{ToolUse("ipython", [], "search(query='class Mail')").to_output(tool_format)}
""".strip()

def search_basic(query: str, directory: str = "."):
    res = subprocess.run(["rga", "--line-number", "--context", "2", "--heading", "-e", query, directory], capture_output=True, text=True)
    results = res.stdout.strip()
    if not results: return "No results found."
    
    filtered_results = "\n".join(line for line in results.split("\n") 
                               if not any(hidden in line for hidden in hidden_files))
    
    if not filtered_results: return "No results found."
    return f"{filtered_results}\nYou can get more context by using the `read` tool with a line_range parameter."

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
    p1.wait()  # Wait for p1 to finish
    
    filtered_output = "\n".join(line for line in output.strip().split("\n")
                              if not any(hidden in line for hidden in hidden_files))
    
    return filtered_output

def preprocess_query(query: str) -> str:
    return query.replace(".", "|") # support class.method queries

def search(query: str):
    query = preprocess_query(query)
    file_contents = subprocess.run(
        ["rga", "--line-number", "--no-heading", "-e", query, '.'],
        capture_output=True,
        text=True
    ).stdout.strip()
    
    file_contents = "\n".join(line for line in file_contents.split("\n")
                            if not any(hidden in line.split(":")[0] for hidden in hidden_files))
    
    file_names = search_file_names(query, '.')
    file_name_results = f"File name matches:\n{file_names}\n" + '-' * 80 + "\n"
    
    parsed = parse_search_results(file_contents)
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

if __name__ == "__main__":
    print(search("def run"))
