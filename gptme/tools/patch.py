"""
Gives the LLM agent the ability to patch text files, by using a adapted version git conflict markers.
"""

from collections.abc import Generator
import difflib
from pathlib import Path

from gptme.tools.file_ctx import FileContext

from gptme.tools.base import ConfirmFunc, Parameter, ToolSpec, ToolUse, get_path
from gptme.util.ask_execute import execute_with_confirmation
from gptme.message import Message

instructions = """
This can be used to edit files, without having to rewrite the whole file.
Try to keep the patch as small as possible.
NOTE: Before submitting a patch, you must request permission to patch using the `request_to_patch` ipython tool in the previous message.
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
Are you sure about your intended change?
1) If not, consider an alternative approach.
2) If so, make your patch small.
> Assistant: Yes, I should update line 13 to include a prompt for the user's name.
{ToolUse("patch", ['src/hello.py', '(13, 13)'], patch_content2).to_output(tool_format)}
> System: Patch applied.
""".strip()


def diff_minimal(original: str, updated: str, strip_context=False) -> str:
    """
    Show a minimal diff of the patch.
    Note that a minimal diff isn't necessarily a unique diff.
    """
    
    diff = list(
        difflib.unified_diff(
            original.splitlines(),
            updated.splitlines(),
            lineterm="",
        )
    )[3:]
    if strip_context:
        # find first and last lines with changes
        markers = [line[0] for line in diff]
        start = min(
            markers.index("+") if "+" in markers else len(markers),
            markers.index("-") if "-" in markers else len(markers),
        )
        end = min(
            markers[::-1].index("+") if "+" in markers else len(markers),
            markers[::-1].index("-") if "-" in markers else len(markers),
        )
        diff = diff[start : len(diff) - end]
    return "\n".join(diff)

def patch(file_path: str | Path, region: tuple[int, int], patch: str) -> Generator[Message, None, None]:
    file_content = open(file_path).read()
    file_lines = file_content.splitlines()
    start, end = region
    file_lines[start-1:end] = patch.splitlines()
    with open(file_path, "w") as file:
        file.write("\n".join(file_lines))
    yield Message("system", f"Patch applied.")

# fake - just to force it to read the section before patching
def request_to_patch(file_path: str, region: tuple[int, int], patch_description: str) -> str:
    ctx = FileContext(file_path)
    if region[1] == -1: region = (region[0], len(ctx.lines))
    ctx.show(line_range=region, scope="line", parents="none")
    patch_region = ctx.stringify()
    return f"""
Approved '{patch_description}' within region:
{patch_region}
Are you sure about your intended change?
1) If not, consider an alternative approach.
2) If so, make your patch small.
""".strip()


def execute_patch(
    updated_code: str | None,
    args: list[str] | None,
    kwargs: dict[str, str] | None,
    confirm: ConfirmFunc,
) -> Generator[Message, None, None]:
    """Patch a file."""
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
    functions=[request_to_patch],
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
    print(request_to_patch("hello.py", region=(11, 14), patch_description="Add a prompt for the user's name"))