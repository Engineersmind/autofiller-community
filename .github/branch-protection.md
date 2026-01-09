# Recommended Branch Protection Rules

Configure these settings in GitHub → Settings → Branches → Add rule for `main`:

## Required Settings

### ✅ Require a pull request before merging
- [x] Require approvals: **1** (increase to 2 for larger teams)
- [x] Dismiss stale pull request approvals when new commits are pushed
- [x] Require review from Code Owners

### ✅ Require status checks to pass before merging
- [x] Require branches to be up to date before merging
- Required checks:
  - `validate-packs`
  - `lint-typescript-sdk`
  - `lint-python-sdk`
  - `validate-openapi`
  - `smoke-eval` (if domain-packs changed)

### ✅ Require conversation resolution before merging

### ✅ Require signed commits (optional but recommended)

### ✅ Do not allow bypassing the above settings

## Optional Settings

### Consider enabling:
- [x] Require linear history (enforces squash/rebase merges)
- [x] Lock branch (for release branches only)

## Setting Up via GitHub CLI

```bash
# Install GitHub CLI if not already installed
# https://cli.github.com/

# Create branch protection rule
gh api repos/{owner}/{repo}/branches/main/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["validate-packs","lint-typescript-sdk","lint-python-sdk","validate-openapi"]}' \
  --field enforce_admins=true \
  --field required_pull_request_reviews='{"dismiss_stale_reviews":true,"require_code_owner_reviews":true,"required_approving_review_count":1}' \
  --field restrictions=null
```

## Why These Rules?

| Rule | Reason |
|------|--------|
| Require PR | Ensures code review and CI runs |
| Require approvals | Catches issues before merge |
| Code Owners | Domain experts review relevant code |
| Status checks | Prevents broken code in main |
| Conversation resolution | Ensures feedback is addressed |
