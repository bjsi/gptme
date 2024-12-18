# reproduce the issue

if [ -z "$1" ]; then
    echo "Usage: $0 <issue>"
    exit 1
fi

export ISSUE=$1
export ALLOW_EDIT="understanding.md,check.py"
export POST_PATCH_MSG="1) Please only write and run one test at a time. 2) If you need more context, use the \`read\` or \`search\` tools."
export PATCH_REQUEST_MSG="Please only write and run one test at a time."

PROMPT1="You are a code explanation checker.
- Given an explanation of the behavior of part of a codebase in \`explanation.md\`, your task is to check whether the explanation is correct.
- Start by reading the explanation in \`explanation.md\`.
- For each bullet point in the explanation, you should read the relevant code using the \`read\` and \`search\` tools. Then, write and run a unit test in \`check.py\` to check whether the explanation is correct.
- Don't change the codebase, only write and run tests to check the explanation."

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