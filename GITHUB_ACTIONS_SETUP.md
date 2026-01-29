# GitHub Actions Setup Guide 🚀

This guide explains how to set up the PR Review Bot using GitHub Actions (no Python required!).

## Advantages of GitHub Actions Approach

✅ **No server needed** - Runs in GitHub's infrastructure  
✅ **Free for public repos** - Included in GitHub free tier  
✅ **Automatic token** - Uses built-in `GITHUB_TOKEN`  
✅ **Easy scheduling** - Built-in cron scheduling  
✅ **Native integration** - Direct access to GitHub API  

## Setup Steps

### 1. Create Slack Webhook

1. Go to [Slack API Apps](https://api.slack.com/apps)
2. Click **"Create New App"** → **"From scratch"**
3. Name: "PR Review Bot" and select your workspace
4. Go to **"Incoming Webhooks"** in the sidebar
5. Toggle **"Activate Incoming Webhooks"** to ON
6. Click **"Add New Webhook to Workspace"**
7. Select the channel for notifications
8. **Copy the webhook URL** (starts with `https://hooks.slack.com/services/...`)

### 2. Add Webhook to GitHub Secrets

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"**
4. Name: `SLACK_WEBHOOK_URL`
5. Value: Paste your Slack webhook URL
6. Click **"Add secret"**

### 3. Add the Workflow File

The workflow file is already in your repository at:
```
.github/workflows/pr-review-slack-notification.yml
```

If you need to add it manually:
1. Create folder: `.github/workflows/`
2. Add the workflow file there
3. Commit and push to GitHub

### 4. Enable GitHub Actions

1. Go to your repository on GitHub
2. Click the **"Actions"** tab
3. If Actions are disabled, click **"I understand my workflows, go ahead and enable them"**
4. You should see **"PR Review Slack Notification"** workflow listed

### 5. Test the Workflow

**Manual Trigger:**
1. Go to **Actions** tab
2. Click **"PR Review Slack Notification"** workflow
3. Click **"Run workflow"** dropdown
4. Select branch (usually `main`)
5. Click **"Run workflow"** button
6. Wait ~30 seconds and check your Slack channel

## Configuration Options

### Schedule Frequency

Edit the cron schedule in the workflow file:

```yaml
on:
  schedule:
    - cron: '0 9-17 * * 1-5'  # Every hour, 9 AM - 5 PM UTC, Mon-Fri
```

**Common schedules:**
- Every hour: `'0 * * * *'`
- Every 2 hours: `'0 */2 * * *'`
- Every day at 9 AM: `'0 9 * * *'`
- Every weekday at 9 AM and 2 PM: `'0 9,14 * * 1-5'`

Use [crontab.guru](https://crontab.guru/) to create custom schedules.

### Trigger on PR Events

The workflow automatically triggers when:
- ✅ A new PR is opened
- ✅ A draft PR is marked as ready for review

You can add more triggers:

```yaml
on:
  pull_request:
    types: 
      - opened
      - ready_for_review
      - review_requested  # When reviewers are assigned
      - reopened          # When PR is reopened
```

### Filter by Labels

To only notify for PRs with specific labels, add this to the script section:

```javascript
// Filter by label
if (!pr.labels.some(label => label.name === 'needs-review')) {
  continue;
}
```

### Mention Users in Slack

To mention Slack users, map GitHub usernames to Slack user IDs:

```javascript
const githubToSlack = {
  'github-username': 'U123ABC456',  // Get from Slack user profile
  'another-user': 'U789XYZ012'
};

const slackMention = githubToSlack[pr.author] 
  ? `<@${githubToSlack[pr.author]}>`
  : pr.author;
```

## Workflow Features

### What It Does

1. **Fetches open PRs** from the repository
2. **Filters out drafts** - only shows PRs ready for review
3. **Checks review status** - shows PRs without approvals
4. **Gets reviewer assignments** - displays who should review
5. **Calculates PR age** - shows how long each PR has been open
6. **Color codes by priority**:
   - 🟢 New (0-3 days)
   - 🟡 Aging (3-7 days)
   - 🔴 Old (7+ days)
7. **Posts to Slack** with rich formatting

### Permissions

The workflow uses the built-in `GITHUB_TOKEN` which has permissions to:
- ✅ Read repository content
- ✅ Read pull requests
- ✅ Read reviews

No additional GitHub token needed!

## Slack Message Format

Example message:

```
📋 Pull Requests Awaiting Review (3)
Repository: `username/repo`
─────────────────────────────

🟢 #42: Add new feature
👤 Author: johndoe
👥 Reviewers: @reviewer1, @reviewer2
📅 Created: 2 days ago
🏷️ Labels: `feature`, `needs-review`
─────────────────────────────

🟡 #38: Fix bug in authentication
👤 Author: janedoe
👥 Reviewers: No reviewers assigned
📅 Created: 5 days ago
─────────────────────────────

Last updated: Jan 29, 2026 10:30:15 AM
```

## Troubleshooting

### Workflow doesn't run

- Check that Actions are enabled in repository settings
- Verify the workflow file is in `.github/workflows/` folder
- Check the workflow syntax is valid (Actions tab shows errors)
- For scheduled runs, note they may be delayed up to 10 minutes

### Slack messages not appearing

- Verify `SLACK_WEBHOOK_URL` secret is set correctly
- Check the webhook URL is active in Slack settings
- Look at workflow logs for error messages (Actions tab → click on workflow run)
- Test webhook manually with curl:
  ```bash
  curl -X POST -H 'Content-type: application/json' \
    --data '{"text":"Test message"}' \
    YOUR_WEBHOOK_URL
  ```

### No PRs showing up

- Check if there are actually open PRs in the repository
- Verify the workflow has permission to read PRs
- Look at the "Get Open PRs" step output in workflow logs

### Rate limits

GitHub Actions has generous limits:
- **GitHub API**: 1,000 requests per hour (authenticated)
- **Slack webhooks**: Very high limits (rarely hit)

The workflow makes ~1 API call per PR, so you can handle hundreds of PRs.

## Cost

- **Public repositories**: FREE ✅
- **Private repositories**: FREE for 2,000 minutes/month
- Each workflow run takes ~30-60 seconds

## Comparison: GitHub Actions vs Python Script

| Feature | GitHub Actions | Python Script |
|---------|----------------|---------------|
| Setup | Easier | More complex |
| Server | Not needed | Required |
| Token | Built-in | Manual |
| Scheduling | Native | External (cron) |
| Flexibility | Limited | High |
| Custom logic | JavaScript | Python |

**Recommendation**: Start with GitHub Actions, switch to Python if you need custom features.

## Advanced: Multiple Repositories

To monitor multiple repositories, either:

1. **Option A**: Add workflow to each repository
2. **Option B**: Create a central repository with workflow that checks multiple repos (requires personal access token)

Example for Option B:

```yaml
- name: Get PRs from multiple repos
  env:
    GITHUB_TOKEN: ${{ secrets.PERSONAL_ACCESS_TOKEN }}
  run: |
    repos=("owner/repo1" "owner/repo2" "owner/repo3")
    for repo in "${repos[@]}"; do
      echo "Checking $repo..."
      # Fetch and process PRs
    done
```

## Support

For issues or questions:
- Check workflow logs in Actions tab
- Review GitHub Actions documentation
- Check Slack API documentation

---

Made with ❤️ for better PR review workflows
