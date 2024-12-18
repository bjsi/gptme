# reproduce the issue

if [ -z "$1" ]; then
    echo "Usage: $0 <issue>"
    exit 1
fi

export ISSUE=$1
export ALLOW_EDIT="understanding.md,check.py"
export POST_PATCH_MSG="1) Please only write and run one test at a time. 2) If you need more context, use the \`read\` or \`search\` tools."
export PATCH_REQUEST_MSG="Please only write and run one test at a time."

SYSTEM_PROMPT="You are designed to help users with programming tasks, such as writing code, debugging, and learning new concepts.
Break down complex tasks into smaller, manageable steps.
You will think step by step when solving a problem, in \`<thinking>\` tags.

You have the ability to self-correct.
If you receive feedback that your output or actions were incorrect, you should:
- acknowledge the mistake
- analyze what went wrong in \`<thinking>\` tags
- provide a corrected response

To create or edit files use the \`patch\` tool.

Use \`<thinking>\` tags to think before you answer."

PROMPT1="You are a code explanation checker.
- Given a detailed explanation of the behavior of part of a codebase in \`explanation.md\`, your task is to check whether the explanation is correct.
- You are naturally a very skeptical person, so you will be very critical of the explanation.
- For each bullet point in the explanation, you should write and run a unit test in \`check.py\` to check whether the explanation is correct.
- Don't change the codebase, only write and run tests to check the explanation.
- You may use the \`search\` and \`read\` tools if you need more context to check or improve the explanation.
- Keep a running log of your \"Current Understanding\" of the code as a nested markdown list in \`understanding.md\` with concise bullet points explaining the current behavior from the entrypoint to the relevant part of the codebase.
- Under that, store a running list of \"Questions to Investigate\"."

# INIT_UNDERSTANDING="# Understanding of the codebase

# # Questions to investigate
# "

# INIT_CHECK_PY="import unittest
# import sys
# import io
# from contextlib import redirect_stdout

# # Import the necessary modules and classes here
# # For example:
# # from your_module import YourClass

# class TestCodeBehavior(unittest.TestCase):
#     def setUp(self):
#         # Set up any necessary objects or configurations
#         pass

#     def tearDown(self):
#         # Clean up after each test
#         pass

#     # Test methods will be added here

# if __name__ == '__main__':
#     unittest.main()
# "

# echo "$INIT_UNDERSTANDING" > understanding.md
# echo "$INIT_CHECK_PY" > check.py

# INIT_MESSAGES='
# [
#     {
#         "role": "user",
#         "content": ""
#     },
#     {
#         "role": "assistant",
#         "content": "Certainly! Let'\''s start by creating the `understanding.md` and `check.py` files.\n\n<thinking>\n1. First, let'\''s request a patch to create the `understanding.md` file and add the requested headings.\n2. Then, we'\''ll request a patch to create the `check.py` file and add the necessary testing boilerplate.\n3. We'\''ll use the `read` tool to examine the relevant functions and tests in detail.\n4. As we go, we'\''ll keep a log of our understanding in `understanding.md`.\n5. We'\''ll also maintain a list of questions to investigate further.\n</thinking>\n\nLet'\''s begin by creating the `understanding.md` file:\n\n```ipython\nrequest_to_patch('\''understanding.md'\'', region=(1, 1), patch_description='\''Initialise the understanding.md file'\'')\n```"
#     },
#     {
#         "role": "system", 
#         "content": "Approved."
#     },
#     {
#         "role": "assistant",
#         "content": "Thank you for approving the creation of the new file. Now, let'\''s apply the patch to create the `understanding.md` file with the desired headings:\n\n```patch understanding.md (1, 1)\n# Understanding of the codebase\n\n# Questions to investigate\n\n```"
#     },
#     {
#         "role": "system",
#         "content": "Approved."
#     },
#     {
#         "role": "assistant", 
#         "content": "Thank you. Now, let'\''s create the `check.py` file:\n\n```ipython\nrequest_to_patch('\''check.py'\'', region=(1, 1), patch_description='\''Initialise the check.py file'\'')\n```"
#     },
#     {
#         "role": "system",
#         "content": "Approved."
#     },
#     {
#         "role": "assistant",
#         "content": "Thank you. Now, let'\''s add the testing setup code to the `check.py` file:\n\n```patch check.py (1, 1)\nimport unittest\nimport sys\nimport io\nfrom contextlib import redirect_stdout\n\n# Import the necessary modules and classes here\n# For example:\n# from your_module import YourClass\n\nclass TestCodeBehavior(unittest.TestCase):\n    def setUp(self):\n        # Set up any necessary objects or configurations\n        pass\n\n    def tearDown(self):\n        # Clean up after each test\n        pass\n\n    # Test methods will be added here\n\nif __name__ == '__main__':\n    unittest.main()\n```"
#     },
#     {
#         "role": "system",
#         "content": "Approved."
#     }
# ]'

gptme -n "check-explanation-issue-$ISSUE" --tools gh,search,read,ipython,patch "$PROMPT1"