# reproduce the issue

if [ -z "$1" ]; then
    echo "Usage: $0 <issue>"
    exit 1
fi

export ISSUE=$1
export ALLOW_EDIT="understanding.md,check.py"
export POST_PATCH_MSG="1) Please only write and run one test at a time. 2) If you need more context, use the \`read\` or \`search\` tools."
export PATCH_REQUEST_MSG="Please only write and run one test at a time."

USER="You are a code explanation checker.
- Given an explanation of the behavior of part of a codebase in \`explanation.md\`, your task is to check whether the explanation is correct.
- Start by reading the explanation in \`explanation.md\`.
- For each bullet point in the explanation, you should read the relevant code using the \`read\` and \`search\` tools. Then, write and run a unit test in \`check.py\` to check whether the explanation is correct.
- Don't change the codebase, only write and run tests to check the explanation.

When editing and running code:
- To create or edit files use the \`patch\` tool.
- To execute code use the \`shell\` tool.
- To run tests use pytest in the \`shell\` tool.

Use \`<thinking>\` tags to think before you answer."

INIT_UNDERSTANDING="# Current understanding

# Questions to investigate
"

INIT_CHECK_PY="import unittest
import sys
import io
from contextlib import redirect_stdout

class TestCodeBehavior(unittest.TestCase):
    def setUp(self):
        # Set up any necessary objects or configurations
        pass

    def tearDown(self):
        # Clean up after each test
        pass

    # Test methods will be added here

if __name__ == '__main__':
    unittest.main()
"

echo "$INIT_UNDERSTANDING" > understanding.md
echo "$INIT_CHECK_PY" > check.py

ASSISTANT_MSG1="Certainly! Let's start by creating the \`understanding.md\` and \`check.py\` files.

<thinking>
1. First, let's do a patch to create the \`understanding.md\` file and add the requested headings.
2. Then, we'll do a patch to create the \`check.py\` file and add the necessary testing boilerplate.
3. We'll use the \`read\` and \`search\` tools to examine the relevant functions and tests in detail.
4. As we go, we'll keep a log of our understanding in \`understanding.md\`.
5. We'll also maintain a list of questions to investigate further.
</thinking>

Let's begin by creating the \`understanding.md\` file:

\`\`\`ipython
request_to_patch('understanding.md', region=(1, 1), patch_description='Initialise the understanding.md file')
\`\`\`"

ASSISTANT_MSG2="Thank you for approving the creation of the new file. Now, let's apply the patch to create the \`understanding.md\` file with the desired headings:

\`\`\`patch understanding.md (1, 1)
$INIT_UNDERSTANDING
\`\`\`"

ASSISTANT_MSG3="Thank you. Now, let's create the \`check.py\` file:

\`\`\`ipython
request_to_patch('check.py', region=(1, 1), patch_description='Initialise the check.py file')
\`\`\`"

ASSISTANT_MSG4="Thank you. Now, let's apply the patch to create the \`check.py\` file:

\`\`\`patch check.py (1, 1)
$INIT_CHECK_PY
\`\`\`"

INIT_MESSAGES="
[
    {
        \"role\": \"user\",
        \"content\": \"\"
    },
    {
        \"role\": \"assistant\",
        \"content\": \"$ASSISTANT_MSG1\"
    },
    {
        \"role\": \"system\", 
        \"content\": \"Approved.\"
    },
    {
        \"role\": \"assistant\",
        \"content\": \"$ASSISTANT_MSG2\"
    },
    {
        \"role\": \"system\",
        \"content\": \"Approved.\"
    },
    {
        \"role\": \"assistant\", 
        \"content\": \"$ASSISTANT_MSG3\"
    },
    {
        \"role\": \"system\",
        \"content\": \"Approved.\"
    },
    {
        \"role\": \"assistant\",
        \"content\": \"$ASSISTANT_MSG4\"
    },
    {
        \"role\": \"system\",
        \"content\": \"Approved.\"
    }
]"

gptme -n "check-explanation-issue-$ISSUE" --tools gh,search,read,ipython,patch --init-messages "$INIT_MESSAGES" "Great, let's continue."