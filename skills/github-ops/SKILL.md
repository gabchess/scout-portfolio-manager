---
name: github-ops
description: Use when managing GitHub repositories, issues, pull requests, CI, releases, or security alerts.
---

# GitHub operations

Use the `gh` CLI for GitHub API operations and verify every state-changing action by reading the target back.

## Operating rules

- Inspect repository, branch, remotes, and current CI before changing anything.
- Prefer a narrow, reversible operation.
- Never put credentials in commands, files, issue bodies, or logs.
- Do not merge, delete, publish, or change repository visibility without explicit authorization.
- For public text, apply the repository's GitHub voice rules.
- After every write, read back the exact repository, issue, pull request, release, or workflow state.

## Common inspection

```bash
gh repo view OWNER/REPO --json nameWithOwner,url,visibility,defaultBranchRef,description
gh run list --repo OWNER/REPO --limit 10
gh pr list --repo OWNER/REPO --state open
gh issue list --repo OWNER/REPO --state open
```

## CI failures

1. Identify the workflow run.
2. Read failed logs.
3. Distinguish a code failure from an environment or flaky failure.
4. Fix the cause rather than rerunning blindly.
5. Re-run only after recording the failure signature.

```bash
gh run list --repo OWNER/REPO --status failure --limit 10
gh run view RUN_ID --repo OWNER/REPO --log-failed
```

## Releases

Before a release, verify the working tree, tests, type checks, security checks, changelog, and public file surface. Create a release only after the exact tag and notes are reviewed.

```bash
gh release create TAG --repo OWNER/REPO --title TAG --generate-notes
```

## Security monitoring

Check Dependabot and secret-scanning alerts by name only. Never retrieve or print secret values.

```bash
gh api repos/OWNER/REPO/dependabot/alerts --jq '.[].security_advisory.summary'
gh api repos/OWNER/REPO/secret-scanning/alerts --jq '.[].state'
```
