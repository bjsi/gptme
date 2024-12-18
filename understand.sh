# understand the issue

ISSUE=$1
SYSTEM_PROMPT="You are a code understanding tool. You will think step by step when solving a problem in \`<thinking>\` tags.
- Gather the context required to deeply understand the following issue: https://github.com/ErikBjare/gptme/issues/\$ISSUE
- Get details about the issue using \`gh\`, and use \`search\` and \`read\` tools to build an understanding of the relevant parts of the codebase and docs.
- Examine each relevant function and related test in detail, expanding context with \`read\` as you go to understand the problem.
- Keep a running log of your \"Current Understanding\" of the code as a nested markdown list with concise bullet points explaining the current behavior from the entrypoint to the relevant part of the codebase.
- Under that, store a running list of \"Questions to Investigate\".
- Ignore any TODOs or questions that aren't relevant to the current issue.
- Do not make changes to the code, only take actions to improve your understanding of the issue."
export ISSUE
gptme -n "understand-issue-$ISSUE" -w @log --system "$SYSTEM_PROMPT" --tools gh,search,read,ipython