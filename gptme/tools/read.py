import os
from typing import Optional
from gptme.tools.base import ToolSpec, ToolUse
from gptme.tools.file_ctx import FileContext


instructions = (
    "Read the content of the given file. The `read` tool takes optional arguments to expand the context of the file. For specialized queries, use the `query` parameter with a tree-sitter query."
)

def read(fp: str, lines: Optional[list[int]] = None, query: Optional[str] = None, names: Optional[list[str]] = None):
   file_ext = os.path.splitext(fp)[1]
   if file_ext != ".py": return open(fp, "r").read() # just cat non-python files
   ctx = FileContext(fp)
   if not lines and not query and not names: ctx.show_skeleton()
   elif lines: ctx.show(lines=lines, scope="full", parents="all")
   elif query: ctx.show(query=query, scope="full", parents="all")
   elif names: ctx.show(names=names, scope="full", parents="all")
   ctx_string = ctx.stringify()
   return f"{fp}\n{ctx_string}\n\n Use further calls to `read` to expand more context if required."

def examples(tool_format):
    return f"""
> User: read file.py
> Assistant: Certainly! Here is the content of file.py:
{ToolUse("ipython", [], "read('file.py')").to_output(tool_format)}

> User: read file.py, focusing on lines of interest 20, 25 and 30.
> Assistant: Certainly! Here is the content of file.py, focusing on and giving context to the function definition at line 20:
{ToolUse("ipython", [], "read('file.py', lines=[20, 25, 30])").to_output(tool_format)}

> User: read file.py, focusing on the "run" and "save" methods.
> Assistant: Certainly! Here is the content of file.py, focusing on and giving context to the "run" and "save" methods:
{ToolUse("ipython", [], "read('file.py', names=['run', 'save'])").to_output(tool_format)}

> User: find everywhere in file.py where the "run" method is called.
> Assistant: Certainly! Here is the content of file.py, focusing on everywhere the "run" method is called using a tree-sitter query:
{ToolUse("ipython", [], "read('file.py', query='(call function: [(identifier) @func.name (attribute attribute: (identifier) @func.name)] (#eq? @func.name \"run\")) @call'").to_output(tool_format)}
""".strip()

tool = ToolSpec(
    name="read",
    desc="Read content from a file.",
    instructions=instructions,
    examples=examples,
    functions=[read]
)