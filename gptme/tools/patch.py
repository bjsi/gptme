"""
Gives the LLM agent the ability to patch text files, by using a adapted version git conflict markers.
"""

from collections.abc import Generator
import difflib
import os
from pathlib import Path
import subprocess
from typing import List, NamedTuple

from gptme.tools.file_ctx import FileContext

from gptme.tools.base import ConfirmFunc, Parameter, ToolSpec, ToolUse, get_path
from gptme.util.ask_execute import execute_with_confirmation
from gptme.message import Message

instructions = """
Use `patch` to edit files. It can also be used to create new files.
Keep the patch as small as possible.
If the patch region overlaps with existing code, it will overwrite the existing code. Include those lines in your patch if you want to keep them.
Before submitting a patch, request permission to patch using the `request_to_patch` ipython tool in the previous message.
""".strip()

patch_content1 = """
class Hello:
    def hello(self):
        name = input("What is your name? ")
        print(f"Hello, {name}!")
"""

patch_content2 = """
        name = input("What is your name? ")
        print(f"Hello, {name}!")
"""

def examples(tool_format):
    return f"""
> User: patch the hello function in `src/hello.py` to ask for the name of the user.
> Assistant: Certainly! I'll patch the file:
{ToolUse("patch", ['src/hello.py', "(11, 13)"], patch_content1).to_output(tool_format)}

> System: You must first request a patch using the `request_to_patch` ipython tool.
> Assistant: Certainly! I'll request a patch first:
{ToolUse("ipython", [], "request_to_patch('src/hello.py', region=(11, 13), patch_description='Add a prompt for the user\'s name')").to_output(tool_format)}
> System: Approved 'Add a prompt for the user's name' within region:
...⋮...
 11│class Hello:
 12│    def hello(self):
 13│        print("Hello World")
...⋮...
Are you sure about your intended change? If not, consider an alternative approach.

> Assistant: Yes, I should update line 13 to include a prompt for the user's name.
{ToolUse("patch", ['src/hello.py', '(13, 13)'], patch_content2).to_output(tool_format)}
> System:
add 'src/hello.py'
[issue_10 c1c1e01] Add a prompt for the user's name
1 file changed, 1 insertion(+), 1 deletion(-)

> User: Actually, I don't want to patch that file.
> Assistant: Okay, I'll revert to the previous commit.
{ToolUse("ipython", [], "revert_to('c1c1e01~1')").to_output(tool_format)}
> System: Patch reverted.

> User: create a new file `ideas.txt` with a TODO list.
> Assistant: Certainly! I'll create the file:
{ToolUse("patch", ['ideas.txt', '(1, 1)'], "TODO: Write a TODO list.").to_output(tool_format)}
> System: Created new file.
""".strip()


def diff_minimal(original: str, updated: str) -> str:
    diff = list(difflib.unified_diff(original.splitlines(), updated.splitlines(), lineterm=""))[3:]
    return "\n".join(diff)

class LintError(NamedTuple):
    line: int
    message: str

def parse_pylint_error(error_line: str) -> LintError | None:
    """Parse a pylint error line to extract line number and message."""
    try:
        # Pylint format is typically: "file.py:line_num: [error_code] message"
        parts = error_line.split(':', 2)
        if len(parts) >= 3:
            line_num = int(parts[1])
            message = parts[2].strip()
            return LintError(line_num, message)
    except (ValueError, IndexError):
        pass
    return None

def run_pylint_errors(file_path: str | Path) -> List[LintError]:
    """Run pylint on a file."""
    file_ext = os.path.splitext(file_path)[1]
    if file_ext not in [".py", ".pyi"]:
        return []
    try:
        result = subprocess.run(
            ['pylint', 
             '--disable=all',  # Disable all checks first
             '--enable=E,F',   # Enable only errors (E) and fatal errors (F)
             str(file_path)],
            capture_output=True,
            text=True,
            check=False
        )
        errors = []
        for line in result.stdout.splitlines():
            if error := parse_pylint_error(line):
                errors.append(error)
        return errors
    except FileNotFoundError:
        return []

_requested = None

def patch(file_path: str | Path, region: tuple[int, int], patch: str) -> Generator[Message, None, None]:
    # Convert to Path object if string
    file_path = Path(file_path)
    start, end = region
    
    # Run pylint before patch
    before_lint = run_pylint_errors(file_path)
    
    # Apply the patch
    original = open(file_path).read()
    original_lines = original.splitlines()
    updated_lines = original_lines[:]
    updated_lines[start-1:end] = patch.splitlines()
    
    # Write the patched content
    with open(file_path, "w") as file:
        file.write("\n".join(updated_lines))
    
    # Run pylint after patch
    after_lint = run_pylint_errors(file_path)
    
    # Filter errors to only those in the patched region
    before_errors = {err for err in before_lint}
    after_errors = {err for err in after_lint}
    
    # Find new errors that weren't present before
    new_errors = after_errors - before_errors
    
    _requested = None
    yield from commit_patch(file_path)

    if new_errors:
        yield Message("system", "⚠️ Warning: New errors introduced in patched region:")
        for error in sorted(new_errors):
            yield Message("system", f"  Line {error.line}: {error.message}")
        yield Message("system", "Based on the errors, you can either correct or revert the patch.")

def commit_patch(file_path: str) -> Generator[Message, None, None]:
    global _requested
    if not _requested: return
    output = ""
    output += subprocess.run(["git", "add", "-v", str(file_path)], check=True, capture_output=True, text=True).stdout
    output += subprocess.run(["git", "commit", "-m", _requested, '-v'], check=True, capture_output=True, text=True).stdout
    _requested = None
    yield Message("system", output)

def revert_to(hash: str) -> Message:
    current_hash = subprocess.run(["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
    subprocess.run(["git", "checkout", hash], check=True, capture_output=True, text=True).stdout
    diff = subprocess.run(["git", "diff", current_hash], check=True, capture_output=True, text=True).stdout
    # subprocess.run(["git", "reset", "--hard", hash], check=True, capture_output=True, text=True).stdout
    output = subprocess.run(["git", "log", "-n", "1", "--oneline"], check=True, capture_output=True, text=True).stdout
    return Message("system", f"Reverted to {output}\n{diff}")

def request_to_patch(file_path: str, region: tuple[int, int], patch_description: str) -> str:
    global _requested
    _requested = patch_description
    if not os.path.exists(file_path):
        return "Approved creation of new file."
    ctx = FileContext(file_path)
    if region[1] == -1: region = (region[0], len(ctx.lines))
    ctx.show(line_range=region, scope="line", parents="none")
    patch_region = ctx.stringify()
    return f"""
Approved '{patch_description}' within region:
{patch_region}
Is this the correct region to overwrite? If not, use `search` or `read` to find the correct region.
""".strip()

def execute_patch(
    updated_code: str | None,
    args: list[str] | None,
    kwargs: dict[str, str] | None,
    confirm: ConfirmFunc,
) -> Generator[Message, None, None]:
    """Patch a file."""
    global _requested
    if not _requested:
        yield Message("system", "You must first request a patch using the `request_to_patch` ipython tool.")
        return
    if not os.path.exists(args[0]):
        with open(args[0], "w") as f: f.write(updated_code)
        yield from commit_patch(args[0])
        return
    region = eval(args[1])
    original_code = "\n".join(open(args[0]).read().splitlines()[region[0] - 1:region[1]])
    yield from execute_with_confirmation(
        updated_code,
        args,
        kwargs,
        confirm,
        execute_fn=lambda *_: patch(args[0], region, updated_code),
        get_path_fn=get_path,
        preview_fn=lambda *_: diff_minimal(original_code, updated_code),
        preview_lang="diff",
        confirm_msg=f"Patch to {get_path(updated_code, args, kwargs)}?",
        allow_edit=True,
    )

tool = ToolSpec(
    name="patch",
    desc="Apply a patch to a file",
    instructions=instructions,
    examples=examples,
    functions=[request_to_patch, revert_to],
    execute=execute_patch,
    block_types=["patch"],
    parse_args=lambda s: [s.split()[1], " ".join(s.split()[2:])],
    parameters=[
        Parameter(
            name="path",
            description="The path to the file to patch",
            type="string",
            required=True,
        ),
        Parameter(
            name="region",
            description="The region to patch",
            type="tuple[int, int]",
            required=True,
        ),
    ]
)
__doc__ = tool.get_doc(__doc__)


if __name__ == "__main__":
    print("shdasoidsand")
    print(revert_to('3c6b670d64a5b').content)
