#!/bin/zsh

issue_body=$(llm -m mistral-7b-instruct-v0 'create a fake github issue')
gh issue create --repo raybellwaves/llm-issue-explorer --title "Generated Issue" --body "$issue_body"
