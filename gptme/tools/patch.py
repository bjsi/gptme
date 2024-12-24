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
""".strip()
if os.environ.get("REQUEST_TO_PATCH"):
    instructions += "\nBefore submitting a patch, request permission to patch using the `request_to_patch` ipython tool in the previous message."

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
    output = f"""
> System:
...⋮...
 11│class Hello:
 12│    def hello(self):
 13│        print("Hello World")
...⋮...
> Assistant: I should update line 13 to include a prompt for the user's name.
{ToolUse("patch", ['src/hello.py', '(13, 13)'], patch_content2).to_output(tool_format)}

> User: Append an if __name__ == "__main__" block at the end of the file.
> Assistant: Okay!
{ToolUse("patch", ['src/hello.py', '(-1, -1)'], "if __name__ == '__main__':\n    Hello().hello()").to_output(tool_format)}

> User: create a new file `ideas.txt` with a TODO list.
> Assistant: Certainly! I'll create the file:
{ToolUse("patch", ['ideas.txt', '(1, 1)'], "TODO: Write a TODO list.").to_output(tool_format)}
""".strip()
    return output

def diff(original: str, updated: str) -> str:
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

# reject_error_types = ['syntax-error', 'invalid-syntax', 'missing-parentheses', 'missing-final-newline', 'mixed-indentation', 'trailing-whitespace', 'unexpected-indentation', 'bad-indentation', 'bad-whitespace', 'mixed-line-endings']

def yield_messages(file_path: str | Path, start: int, patch: str, new_errors: List[LintError]) -> Generator[Message, None, None]:
    global _requested
    _requested = None
    yield from commit_patch(file_path)
    ctx = FileContext(file_path)
    ctx.show(line_range=(start, start + len(patch.splitlines()) - 1), scope="line", parents="none")
    diff = ctx.stringify()
    yield Message("system", f"Updated region:\n{diff}")
    if new_errors:
        yield Message("system", "⚠️ Warning: New errors introduced in patched region:")
        for error in sorted(new_errors):
            yield Message("system", f"  Line {error.line}: {error.message}")
    if os.environ.get("POST_PATCH_MSG"): yield Message("system", os.environ.get("POST_PATCH_MSG"))
    # yield Message("system", "If you notice errors, you can correct them or revert the patch using the `revert_to` tool.")

def patch(file_path: str | Path, region: tuple[int, int], patch: str) -> Generator[Message, None, None]:
    global _requested
    if os.environ.get("REQUEST_TO_PATCH") and not _requested:
        yield Message("system", "You must first request a patch.")
        return

    # Convert to Path object if string
    file_path = Path(file_path)
    start, end = region
    # Run pylint before patch
    before_lint = run_pylint_errors(file_path)

    # Handle new file creation
    if not file_path.exists():
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(patch)  # Remove trailing newline for new files
        yield from yield_messages(file_path, start, patch, [])
        return

    # Read existing file
    with open(file_path, encoding="utf-8") as f:
        content = f.read()
    original_lines = content.splitlines()
    
    # Handle (-1, -1) case - append to end
    if (start == -1 or start > len(original_lines)):
        start = len(original_lines) + 1
        end = start
    
    # Handle (<=1, -1) case - replace entire file
    elif start <= 1 and end == -1:
        updated_content = patch
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(updated_content)
        yield from yield_messages(file_path, start, patch, [])
        return
    
    if end == -1: end = len(original_lines) + 1
    # Preserve trailing newline if it existed
    had_trailing_newline = content.endswith("\n")
    # Preserve trailing newline if it existed
    had_trailing_newline = content.endswith("\n")
    
    # Apply the patch
    updated_lines = original_lines[:]
    if start > len(updated_lines):
        updated_lines.append(patch)
    else:
        # Handle empty string patch by converting it to a single empty line
        patch_lines = patch.splitlines() if patch else [""]
        updated_lines[start-1:end] = patch_lines
    
    # Write the patched content
    updated_content = "\n".join(updated_lines)
    if had_trailing_newline:
        updated_content += "\n"
        
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(updated_content)
    
    # Run pylint after patch
    after_lint = run_pylint_errors(file_path)
    
    # Filter errors to only those in the patched region
    before_errors = {err for err in before_lint}
    after_errors = {err for err in after_lint}
    
    # Find new errors that weren't present before
    new_errors = after_errors - before_errors
    yield from yield_messages(file_path, start, patch, new_errors)
    

def commit_patch(file_path: str) -> Generator[Message, None, None]:
    global _requested
    if not _requested: return
    output = ""
    output += subprocess.run(["git", "add", "-v", str(file_path)], check=True, capture_output=True, text=True).stdout
    output += subprocess.run(["git", "commit", "-m", _requested, '-v'], check=True, capture_output=True, text=True).stdout
    _requested = None
    yield Message("system", output)

def revert_to(commit_hash: str) -> Message:
    current_hash = subprocess.run(["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
    subprocess.run(["git", "checkout", commit_hash], check=True, capture_output=True, text=True).stdout
    diff = subprocess.run(["git", "diff", current_hash], check=True, capture_output=True, text=True).stdout
    subprocess.run(["git", "reset", "--hard", commit_hash], check=True, capture_output=True, text=True).stdout
    output = subprocess.run(["git", "log", "-n", "1", "--oneline"], check=True, capture_output=True, text=True).stdout
    return Message("system", f"Reverted to {output}\n{diff}")

def allow_edit(file_path: str) -> bool:
    allow_edit = os.environ.get("ALLOW_EDIT")
    if not allow_edit: return True
    allowed = allow_edit.split(',')
    file_path = str(file_path)  # Convert Path to string if needed
    for allowed_path in allowed:
        # Check if file matches exactly or is under allowed directory
        if file_path == allowed_path or file_path.startswith(allowed_path + '/'):
            return True
    return False

def request_to_patch(file_path: str, region: tuple[int, int], patch_description: str) -> str:
    global _requested
    _requested = patch_description
    if not allow_edit(file_path):
        return f"You are not allowed to edit this file.\nYou are allowed to edit:\n{'\n'.join(os.environ.get('ALLOW_EDIT').split(','))}"
    if not os.path.exists(file_path):
        output = ""
        if os.environ.get("PATCH_REQUEST_MSG"): output += f"{os.environ.get('PATCH_REQUEST_MSG')}\n"
        output += "Approved creation of new file."
        return f"{output}"
    ctx = FileContext(file_path)
    if region[1] == -1: region = (region[0], len(ctx.lines))
    # if region[0] == -1: region = (len(ctx.lines), region[1])
    ctx.show(line_range=region, scope="line", parents="none")
    patch_region = ctx.stringify()
    reminders = "Is this the correct region to overwrite? If not, use `search` or `read` to find the correct region."
    if os.environ.get("PATCH_REQUEST_MSG"): reminders += f"\n{os.environ.get('PATCH_REQUEST_MSG')}"
    return f"""
Approved '{patch_description}' within region:
{patch_region}
{reminders}
""".strip()

def execute_patch(
    updated_code: str | None,
    args: list[str] | None,
    kwargs: dict[str, str] | None,
    confirm: ConfirmFunc,
) -> Generator[Message, None, None]:
    """Patch a file."""
    global _requested
    if os.environ.get("REQUEST_TO_PATCH") and not _requested:
        yield Message("system", "You must first request a patch.")
        return
    if not os.path.exists(args[0]):
        with open(args[0], "w") as f: f.write(updated_code)
        yield from commit_patch(args[0])
        return
    
    with open(args[0], 'r') as f:
        code_lines = f.read().splitlines()
    region = eval(args[1])
    if region[0] == -1:
        region = (len(code_lines), len(code_lines))
        diff_preview = diff("", updated_code)
    else:
        original_code = "\n".join(code_lines[region[0] - 1:region[1]])
        diff_preview = diff(original_code, updated_code)
    yield from execute_with_confirmation(
        updated_code,
        args,
        kwargs,
        confirm,
        execute_fn=lambda *_: patch(args[0], region, updated_code),
        get_path_fn=get_path,
        preview_fn=lambda *_: diff_preview,
        preview_lang="diff",
        confirm_msg=f"Patch to {get_path(updated_code, args, kwargs)}?",
        allow_edit=True,
    )

functions = [request_to_patch, revert_to]
if not os.environ.get("REQUEST_TO_PATCH"):
    functions.remove(request_to_patch)

tool = ToolSpec(
    name="patch",
    desc="Apply a patch to a file",
    instructions=instructions,
    examples=examples,
    # functions=functions,
    execute=execute_patch,
    block_types=["patch"],
    parse_args=lambda s: [s.split()[0], " ".join(s.split()[1:])],
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