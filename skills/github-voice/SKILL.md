---
name: github-voice
description: Use when writing or auditing GitHub-visible text.
---

# GitHub voice

Keep public GitHub writing concise, specific, and inspectable.

## Hard rules

- Never include local absolute paths, private repository names, internal handoff notes, agent rosters, credentials, or customer data.
- Do not include `Co-Authored-By` lines for assistants or internal agents.
- Do not overclaim production readiness, security, performance, or adoption.
- Link the artifact instead of praising it.
- Name important limits next to the claim they qualify.
- Use tables for project lists longer than three entries.
- Keep each project-table cell to one sentence.
- Avoid em dashes in GitHub-visible text.

## Useful checks

```bash
grep -nE '/Users/|\.remember|\.arcana|Co-Authored-By|private context' <draft-file>
grep -niE 'world.?class|cutting.?edge|passionate|innovative|robust|comprehensive|seamless|powerful|best.?in.?class' <draft-file>
```

Both checks should return no matches. Review false positives manually when a technical term is legitimate.

## Style

1. Lead with a number, mechanism, or explicit limit.
2. Put one claim on each line.
3. Give each project row one hard specific.
4. Cut sentences that would remain true if the project did not exist.
5. Prefer concrete verbs and observable behavior.
6. Keep release notes user-visible and honest.

## Commit messages

Use Conventional Commits with a subject under 72 characters:

```text
feat(adapter): add bounded portfolio observation
```

## Pull requests

Use these sections:

```markdown
## Summary
- What changed

## Test plan
- [ ] Exact verification command
- [ ] Relevant behavior checked
```
