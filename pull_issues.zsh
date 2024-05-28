#!/bin/zsh

REPO="raybellwaves/llm-issue-explorer"

issue_count=$(gh issue list --repo $REPO --json number | jq '. | length')

for ((i=1; i<=issue_count; i++)); do
  gh issue view --repo $REPO $i --json assignees,author,body,closed,closedAt,comments,createdAt,id,labels,milestone,number,projectCards,projectItems,reactionGroups,state,title,updatedAt,url > "issue_detail_$i.json"
done
