# GitHub Actions Setup for Claude Code

## Overview
This document explains the GitHub Actions workflow setup for automating code modifications using Claude Code on GitHub.

## Current Status

### Workflow File Location
- **File**: `.github/workflows/claude.yml`
- **Status**: Pending merge in PR #102
- **Repository**: https-deeplearning-ai/starting-ragchatbot-codebase

### PR #102 Details
- **Title**: Add Claude Code GitHub Actions workflow
- **State**: OPEN
- **URL**: https://github.com/https-deeplearning-ai/starting-ragchatbot-codebase/pull/102
- **Changes**: Adds Claude Code automation workflow with debug features

## How to Use Claude Code on GitHub

### Prerequisites
1. PR #102 must be merged to enable the workflow
2. `ANTHROPIC_API_KEY` secret must be configured in the repository

### Setting Up the Secret

Go to your GitHub repository → Settings → Secrets and variables → Actions → New repository secret

- **Name**: `ANTHROPIC_API_KEY`
- **Value**: Your Anthropic API key (generate with `ztoken token -n zllm`)

### Triggering Claude Code

Claude Code can be triggered in three ways:

#### 1. Create an Issue Mentioning @claude
```
Title: New feature or fix description
Body: Include detailed requirements and mention @claude
```

#### 2. Comment @claude on an Existing Issue
Simply comment on any issue with:
```
@claude please implement the changes described above
```

#### 3. Comment @claude on a Pull Request
Comment on a PR with:
```
@claude please fix the failing tests and add documentation
```

## Workflow Features

### Debug Output
The workflow includes several debug features to help troubleshoot issues:

1. **Secret Verification**
   - Checks if `ANTHROPIC_API_KEY` is properly set
   - Fails immediately if secret is missing

2. **API Connectivity Check**
   - Tests connection to api.anthropic.com
   - Helps diagnose network issues

3. **Full Output Logging**
   - Enabled with `show_full_output: true`
   - Shows complete Claude Code execution details
   - Useful for debugging failed runs

### Workflow Permissions
The workflow is configured with proper permissions:

```yaml
permissions:
  contents: write        # Can commit changes
  pull-requests: write   # Can create/update PRs
  issues: write          # Can comment on issues
  id-token: write        # For authentication
  actions: read          # Can read CI results
```

## Common Issues and Solutions

### Issue: Workflow Not Triggering
**Cause**: PR #102 not yet merged
**Solution**: Merge PR #102 to enable the workflow

### Issue: 401 Unauthorized Error
**Cause**: API token expired (tokens valid for 1 hour)
**Solution**:
1. Generate a fresh token: `ztoken token -n zllm`
2. Update repository secret with new token
3. Retry Claude Code request

### Issue: Workflow Shows "No Permissions"
**Cause**: Workflow permissions not set to write
**Solution**: Check that workflow has proper permissions in `.github/workflows/claude.yml`

## Viewing Workflow Runs

Go to your repository → Actions tab to see:
- All workflow runs
- Execution logs and output
- Success/failure status
- Claude Code execution details (with `show_full_output: true`)

## Testing the Workflow

### Test Case: New Chat Button Feature
1. Merge PR #102
2. Set up `ANTHROPIC_API_KEY` secret
3. Go to Issue #101: "Test Claude Code with debug output"
4. Comment: `@claude please implement the changes described in this issue`
5. Workflow should trigger and Claude Code should:
   - Implement the New Chat button
   - Add styling for dark/light theme compatibility
   - Create a pull request with the changes

## Example Workflow Run Output

When the workflow runs successfully, you'll see:

```
✓ ANTHROPIC_API_KEY is set
Checking API endpoint reachability...
HTTP/1.1 200 OK
...
[Claude Code execution output]
...
✅ Pull request created with implementation
```

## Next Steps

1. **Merge PR #102** to the main repository
2. **Configure ANTHROPIC_API_KEY** secret in repository settings
3. **Test with Issue #101** to verify Claude Code works
4. **Use on other tasks** by creating issues/PRs with @claude mentions

---

*Last Updated: 2025-12-31*
*Setup by: Claude Code*
