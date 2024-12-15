from typing import Union
import uuid

from gptme.tools.base import ToolSpec, ToolUse
from gptme.tools.file_context import FileContext


instructions = (
    "Request access to the patch tool to be apply a patch to a file."
)

def request_to_patch(file_path: str, line_range: tuple[int, int]) -> str:
    ctx = FileContext(file_path)
    if line_range[1] == -1: line_range = (line_range[0], len(ctx.lines))
    ctx.show(line_range=line_range, scope="line", parents="none")
    patch_region = ctx.stringify()
    return f"Approved. Apply the patch after confirming the region is correct:\n{patch_region}\n"

def examples(tool_format):
    return f"""
> User: submit a request to patch the "run" method between lines 10 and 15 in file "file.py"
> Assistant: Certainly! I'll use the ipython function `request_to_patch` to get permission to patch the file.
{ToolUse("ipython", [], "request_to_patch('file.py', line_range=(10, 15))").to_output(tool_format)}
""".strip()

# all fake - just to force it to read the section before patching

tool = ToolSpec(
    name="request_to_patch",
    desc="Request to patch a file. Specify the file path and the location of the patch as a range of lines.",
    instructions=instructions,
    examples=examples,
    functions=[request_to_patch],
)