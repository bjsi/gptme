# understand the issue

if [ -z "$1" ]; then
    echo "Usage: $0 <issue>"
    exit 1
fi

export ISSUE=$1
export ALLOW_EDIT="understanding.md"

PROMPT1="You are a code understanding tool. You will think step by step when solving a problem in \`<thinking>\` tags.
- Gather the context required to deeply understand the following issue: https://github.com/ErikBjare/gptme/issues/\$ISSUE
- Get details about the issue using \`gh\`, and use \`search\` and \`read\` tools to build an understanding of the relevant parts of the codebase and docs.
- Examine each relevant function and related test in detail, expanding context with \`read\` as you go to understand the problem.
- Keep a running log of your \"Current Understanding\" of the code as a nested markdown list in \`understanding.md\` with concise bullet points explaining the current behavior from the entrypoint to the relevant part of the codebase.
- Under that, store a running list of \"Questions to Investigate\".
- Ignore any TODOs or questions that aren't relevant to the current issue.
- Don't make code changes - only update the \`understanding.md\` file."

# PROMPT2="Assistant:
# Certainly! I'll gather the context required to draft a solution for the issue https://github.com/ErikBjare/gptme/issues/$ISSUE.
# Let's start by examining the issue details and then explore the relevant parts of the codebase.

# <thinking>
# 1. First, let's create a new file \`understanding.md\` to store our understanding and running list of questions.
# 2. Then, let's view the issue details using the \`gh\` tool.
# 3. Then, we'll use the \`search\` and \`read\` tools to find relevant parts of the codebase and examine the relevant functions and tests in detail.
# 4. As we go, we'll keep a log of our understanding in \`understanding.md\`.
# 5. We'll also maintain a list of questions to investigate further.
# </thinking>

# Let's begin by creating the \`understanding.md\` file.

# ```ipython
# request_to_patch('understanding.md', region=(1, 1), patch_description='Create a new file to store our understanding and running list of questions.')
# ```"

# PROMPT3="System:
# Approved creation of new file."

# PROMPT4="Assistant:
# Thanks for approving the creation of the \`understanding.md\` file.

# Now let's create the file:

# ```patch understanding.md (1, 1)
# \# Current Understanding

# \# Questions to Investigate
# ```"

gptme -n "understand-issue-$ISSUE" --tools gh,search,read,ipython,patch "$PROMPT1"
