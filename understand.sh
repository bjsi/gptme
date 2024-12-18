# understand the issue

if [ -z "$1" ]; then
    echo "Usage: $0 <issue>"
    exit 1
fi

export ISSUE=$1
export ALLOW_EDIT="understanding.md"
export POST_PATCH_MSG="Are you sure your explanation and questions are relevant to issue $ISSUE?"

PROMPT1="You are a code understanding tool. You will think step by step when solving a problem in \`<thinking>\` tags.
- Gather the context required to draft a solution to the following issue: https://github.com/ErikBjare/gptme/issues/$ISSUE
- Get details about the issue using \`gh\`, and use \`search\` and \`read\` tools to build an understanding of the relevant parts of the codebase.
- Examine each relevant function in detail, expanding context with \`read\` as you go to understand the problem.
- Keep a running log of your \"Current Understanding\" of the code as a nested markdown list in \`understanding.md\` with concise bullet points explaining the current behavior from the entrypoint to the relevant part of the codebase.
- Under that, store a running list of \"Questions to Investigate\".
- Ignore anything that isn't relevant to issue $ISSUE.
- Don't make code changes - only overwrite the \`understanding.md\` file."

gptme -n "understand-issue-$ISSUE" --tools gh,search,read,ipython,patch "$PROMPT1"
