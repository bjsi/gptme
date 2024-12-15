issue_instructions = """Your task is to write a plan and gather the context required to solve the following issue: https://github.com/ErikBjare/gptme/issues/108. Setup your workspace. Clone the repo, set up a venv and figure out how to install deps. Get details about the issue using `gh issue view`. Use search tools to build an understanding of the problem. Save the necessary context snippets from the search results into your repo map. Once you have fully understood the problem and gathered the necessary context, fill out the Problem, Expected Output, Current Output form. In the problem section, summarize the problem and detail the solution plan. In the expected expected output section can you give an example of the expected output/result. In the current output section can you show an example of how the current version is failing (this may involve running code)."""
plan_issue_instructions2 = """
You are a code implementation planner.
Gather the context required to solve the following issue: https://github.com/ErikBjare/gptme/issues/326.
Your task is only to create the plan to solve the issue.
Get details about the issue using `gh issue view` and use `search` and `read` tools to build an understanding of the relevant parts of the codebase. Prefer `read` over `cat`.
If the issue is not clear, you need to take extra care to gather the context required to solve the issue.
Examine each relevant function in detail, explaining its current behavior and limitations and identify specific lines of code that need to be modified.
Propose concrete changes, including updated function signatures, logic modifications and any new functions or classes that might be required.
Search the codebase for tests that may be affected or need to be added with your proposed changes.
Continue gathering context until you can describe the exact changes needed in the codebase. Only write the final implementation plan after a thorough analysis.
Once you have fully understood the problem write the implementation plan as step-by-step bullet points on the relevant parts of the code, including tests, using the `add_plan_details` tool.
"""
implement_issue_instructions = """
Good morning Jake, your task is to implement the solution to the following issue: https://github.com/ErikBjare/gptme/issues/326.
Use `gh issue view` to get details about the issue.
Then use the plan in ./plan-108.txt to guide your implementation.
Whenever you've made a change that is testable, you should either run existing tests or add new tests to verify the change. Do not just wait until the end to run tests.
"""
