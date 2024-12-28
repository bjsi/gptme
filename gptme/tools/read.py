import json
import os
from typing import Optional
from gptme.tools.base import ToolSpec, ToolUse
from gptme.tools.file_ctx import FileContext


instructions = "Read the content in the given file."

# stores all context accessed through `read` calls
# filled up during the `Understand` step
# passed to the `Reproduce` and `Fix` steps
_cache: dict[str, FileContext] = {} # file -> FileContext

def reset_file_read_cache():
   _cache.clear()

def save_file_read_cache(ignore_files: Optional[list[str]] = None):
   stringified = {k: v.stringify() for k, v in _cache.items() if k not in ignore_files}
   with open("read_cache.json", "w") as f:
      json.dump(stringified, f)

def read(fp: str, line_range: Optional[list[int]] = None, query: Optional[str] = None, names: Optional[list[str]] = None):
  file_ext = os.path.splitext(fp)[1]
  ctx = FileContext(fp)
  if file_ext != ".py":
     ctx.show_all() # just cat non-python files
  else:
    ctx = ctx.show_skeleton() # always include skeleton
    if not line_range and not query and not names: ctx.show_skeleton()
    elif line_range: ctx.show(line_range=line_range, scope="full", parents="all")
    elif query: ctx.show(query=query, scope="full", parents="all") # not documneted
    elif names: ctx.show(names=names, scope="full", parents="all")
  # udpate cache
  if fp not in _cache: _cache[fp] = ctx
  else: _cache[fp].merge(ctx)
  # output
  ctx_string = ctx.stringify()
  output = f"{fp}\n{ctx_string}\nUse further calls to `read` or `search` to expand more context if required."
  return output

def examples(tool_format):
    return f"""
> User: read file.py
> Assistant:
{ToolUse("ipython", [], "read('file.py')").to_output(tool_format)}

> User: read file.py, focusing on the "run" and "save" methods.
> Assistant: Certainly! Here is the content of file.py, focusing on and giving context to the "run" and "save" methods:
{ToolUse("ipython", [], "read('file.py', names=['run', 'save'])").to_output(tool_format)}

> User: read file.py, between lines 20 and 30.
> Assistant: Certainly! Here is the content of file.py between lines 20 and 30:
{ToolUse("ipython", [], "read('file.py', line_range=[20, 30])").to_output(tool_format)}
""".strip()

tool = ToolSpec(
    name="read",
    desc="Read content from a file.",
    instructions=instructions,
    examples=examples,
    functions=[read],
)

if __name__ == "__main__":
    print(read('gptme/cli.py', line_range=[140, 160]))