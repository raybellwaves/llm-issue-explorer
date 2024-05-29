#!/bin/zsh
#
#./utils.zsh

# REPO="raybellwaves/llm-issue-explorer"
# Create a fake issue
# issue_body=$(llm -m mistral-7b-instruct-v0 'create a fake github issue')
# gh issue create --repo raybellwaves/llm-issue-explorer --title "Generated Issue" --body "$issue_body"

issue_count=$(gh issue list --repo raybellwaves/llm-issue-explorer --json number | jq '. | length')
for i in $(seq 1 30); do
    j=$((i + issue_count))
    gh issue create --repo raybellwaves/llm-issue-explorer --title "Issue ${j}" --body "Body ${j}"
    sleep 5
done
