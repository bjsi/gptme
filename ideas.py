issue_instructions = """Your task is to write a plan and gather the context required to solve the following issue: https://github.com/ErikBjare/gptme/issues/108. Setup your workspace. Clone the repo, set up a venv and figure out how to install deps. Get details about the issue using `gh issue view`. Use search tools to build an understanding of the problem. Save the necessary context snippets from the search results into your repo map. Once you have fully understood the problem and gathered the necessary context, fill out the Problem, Expected Output, Current Output form. In the problem section, summarize the problem and detail the solution plan. In the expected expected output section can you give an example of the expected output/result. In the current output section can you show an example of how the current version is failing (this may involve running code)."""
plan_issue_instructions2 = """
You are a code implementation planner. There are three parts to your job.

# 1. Research
- Gather the context required to draft a solution to the following issue: https://github.com/ErikBjare/gptme/issues/202
- Get details about the issue using `gh issue view`, and use `search` and `read` tools to build an understanding of the relevant parts of the codebase and docs.
- Examine each relevant function and related test in detail, expanding context with `read` as you go to understand the problem.
- Search the codebase for tests that may be affected or need to be added with your proposed changes.

# 2. Draft implementation
- Implement a simplified version of the solution in a draft.py file. Don't edit the main codebase, only the draft.py file.
- The draft implementation should be a minimal working example that demonstrates the solution.
- The draft implementation file draft.py must contain unit tests that verify your plan.
- Keep running the tests and editing your draft until the tests pass.

# 3. Plan Writing
- Once you have a working draft implementation, write a plan for the exact changes needed in the codebase.
- Write the implementation plan as step-by-step bullet points on the relevant parts of the code, including test files, using the `add_plan_details` tool.
"""
implement_issue_instructions = """
Good morning Jake, your task is to implement the solution to the following issue: https://github.com/ErikBjare/gptme/issues/326.
Use `gh issue view` to get details about the issue, then use the plan in ./plan.txt to guide your implementation.
When implementing the solution, you should follow this process:

# 1. Make a small, testable change to the codebase.
- Make a small testable change to the codebase, following the plan in ./plan.txt. To make your code easily testable, consider implementing changes as new functions.
- Create a new test to verify the specific change you made.
- Do not move on to the next step until you have passed the test.
- Repeat these steps until you have implemented the entire solution.

# 2. Run tests
- Run all tests you added to verify the solution.
- Run any relevant tests in the codebase to verify the solution.
"""
