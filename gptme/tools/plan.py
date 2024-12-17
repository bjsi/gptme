from typing import Dict
from gptme.tools.base import ToolSpec, ToolUse
from gptme.tools.file_ctx import FileContext


class Plan:
    """A plan to implement a specific task in a repository."""
    def __init__(self):
        self.file_context_map: Dict[str, FileContext] = {}

    def write_plan(self, file_line_comment_map: Dict[str, Dict[int, str]]):
        for file_path, line_comment_map in file_line_comment_map.items():
            ctx = FileContext(file_path)
            lines = line_comment_map.keys()
            ctx = ctx.show(lines=lines, scope="full", parents="all").add_comments(line_comment_map)
            if file_path not in self.file_context_map: self.file_context_map[file_path] = ctx
            else: self.file_context_map[file_path].merge(ctx)
        return self

    def stringify(self, comment_prefix: str = ''):
        out = ""
        for file_path, context in self.file_context_map.items():
            out += f"{'-' * 100}\n"
            out += f"{file_path}\n{context.stringify(comment_prefix=comment_prefix)}\n"
        return out

_plan: Plan | None = None

def get_plan() -> Plan:
    global _plan
    if _plan is None:
        _plan = Plan()
    return _plan

def add_plan_details(file_line_comment_map: Dict[str, Dict[int, str]]):
    updated_map = {} # Update any line numbers of 0 to 1 in the comment map
    for file, line_comments in file_line_comment_map.items():
        updated_map[file] = {max(1, line): comment for line, comment in line_comments.items()}
    get_plan().write_plan(updated_map)

def print_implementation_plan(issue_number: int):
    print(get_plan().stringify(f" TODO(jake|{issue_number}):"))

instructions = """Write up an implementation plan for a specific issue by adding inline comments in the codebase."""

def examples(tool_format):
    return f"""
...⋮...
  7│class Hello:
  8│    def hello(self):
  9│        print("Hello World")
...⋮...
 20│if __name__ == "__main__":
 21│    hello = Hello()
 22│    hello.hello()
> User: write a plan for issue 76 to update the hello method to greet the user by name
> Assistant:
{ToolUse("add_plan_details", [], "add_plan_details({'file.py': {8: 'Update the method signature to accept a name argument\nModify the print statement to greet the user by name'}})").to_output(tool_format)}
> System:
...⋮...
   │    # Update the method signature to accept a name argument
   │    # Modify the print statement to greet the user by name
  8│    def hello(self):
  9│        print("Hello World")
...⋮...
""".strip()

tool = ToolSpec(
    instructions=instructions,
    examples=examples,
    name="add_plan_details",
    desc="Write up an implementation plan for a specific issue inline in the codebase. Do this last after you've searched and read the codebase.",
    functions=[add_plan_details],
)