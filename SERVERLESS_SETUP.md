# Serverless Eye Emoji Setup (No Webhook Server Required) 👀

This guide shows how to implement the PR review claim feature **without any external webhook server** using only GitHub Actions and PR comments.

## How It Works (Serverless)

1. 👉 Bot posts PR notification to Slack with "Review This" button
2. 🔘 Team member clicks button (opens PR on GitHub)
3. 💬 Team member comments `/claim` or `👀` on the PR
4. ⚡ GitHub Actions detects the comment
5. ✅ Auto-assigns reviewer on GitHub PR
6. 📝 Adds status comment: "PR is being reviewed by @username"
7. 👍 Reacts to the claim comment with 👍 and 👀
8. 📢 Posts confirmation to Slack (optional)

**No server needed! Everything runs in GitHub Actions.**

## Setup (5 Minutes)

### Step 1: Workflow Files Already Created ✅

The following workflows are already in your repository:

1. **[pr-review-slack-notification.yml](.github/workflows/pr-review-slack-notification.yml)** - Posts PRs to Slack
2. **[handle-pr-claim.yml](.github/workflows/handle-pr-claim.yml)** - Handles `/claim` comments

### Step 2: Slack Webhook (Already Set Up)

If you followed the GitHub Actions setup, you already have `SLACK_WEBHOOK_URL` configured.

If not:
1. Go to [api.slack.com/apps](https://api.slack.com/apps)
2. Create app → Incoming Webhooks → Add webhook
3. Add `SLACK_WEBHOOK_URL` to GitHub Secrets

### Step 3: Enable GitHub Actions

1. Go to your repository on GitHub
2. Click **Actions** tab
3. Enable Actions if not already enabled
4. Both workflows should appear in the list

### Step 4: Test It!

**Option A: Test with existing PR**
1. Go to any open PR in your repository
2. Comment: `/claim` or `👀`
3. Watch the magic happen:
   - ✅ You'll be added as reviewer
   - 📝 Bot comments: "PR is being reviewed by @you"
   - 👍 Your comment gets reactions
   - 📢 Slack notification (if configured)

**Option B: Create test PR**
1. Make a small change and create PR
2. PR notification will appear in Slack
3. Click "👀 Review This" button
4. Comment `/claim` on the PR
5. See the automated response

## Claim Keywords

Any of these will trigger the review claim:

- `/claim`
- `👀` (just the emoji)
- `/review`
- `reviewing this`

## Features

### ✅ What It Does

- **Assigns you as reviewer** on the PR
- **Adds status comment** so everyone knows you're reviewing
- **Reacts to your comment** with 👍 and 👀
- **Notifies Slack** (optional) with confirmation
- **Fully automated** - no manual steps

### 🎯 What Shows in Slack

Original PR notification now includes:
```
🟢 #42: Add new feature
👤 Author: johndoe
👥 Reviewers: @reviewer1
📅 Created: 2 days ago

👀 To claim this review, comment `/claim` or 👀 on the PR
[👀 Review This] ← Button that opens PR
```

After claiming:
```
👀 PR Review Claimed

@alice is now reviewing PR #42: Add new feature
Repository: `owner/repo`
```

### 📝 What Shows on GitHub

On the PR, bot adds comment:
```
👀 PR is now being reviewed by @alice

Claimed via comment. Review status will be tracked.
```

Plus:
- ✅ You're added to "Reviewers" section
- 👍 Your `/claim` comment gets 👍 and 👀 reactions
- 📊 Shows in PR timeline

## Advanced Customization

### Custom Claim Keywords

Edit [handle-pr-claim.yml](.github/workflows/handle-pr-claim.yml):

```yaml
- name: Check if claim comment
  id: check-claim
  uses: actions/github-script@v7
  with:
    script: |
      const comment = context.payload.comment.body.toLowerCase().trim();
      const claimKeywords = [
        '/claim', 
        '👀', 
        '/review',
        'reviewing this',
        'i got this',      # Add your own
        'on it'            # Add your own
      ];
```

### Prevent Multiple Claims

Add logic to check if PR already has reviewers:

```yaml
- name: Check if already claimed
  id: check-existing
  uses: actions/github-script@v7
  with:
    script: |
      const { data: pr } = await github.rest.pulls.get({
        owner: context.repo.owner,
        repo: context.repo.repo,
        pull_number: context.issue.number
      });
      
      if (pr.requested_reviewers.length > 0) {
        await github.rest.issues.createComment({
          owner: context.repo.owner,
          repo: context.repo.repo,
          issue_number: context.issue.number,
          body: '⚠️ This PR already has reviewers assigned.'
        });
        return false;
      }
      return true;
```

### Auto-assign Based on Files Changed

Assign specific reviewers based on what files were modified:

```yaml
- name: Smart Assignment
  uses: actions/github-script@v7
  with:
    script: |
      const { data: files } = await github.rest.pulls.listFiles({
        owner: context.repo.owner,
        repo: context.repo.repo,
        pull_number: context.issue.number
      });
      
      const codeOwners = {
        'frontend/': ['frontend-lead'],
        'backend/': ['backend-lead'],
        'docs/': ['tech-writer']
      };
      
      let suggestedReviewer = null;
      for (const file of files) {
        for (const [path, owners] of Object.entries(codeOwners)) {
          if (file.filename.startsWith(path)) {
            suggestedReviewer = owners[0];
            break;
          }
        }
      }
      
      // Add suggested reviewer as additional reviewer
      if (suggestedReviewer) {
        await github.rest.pulls.requestReviewers({
          owner: context.repo.owner,
          repo: context.repo.repo,
          pull_number: context.issue.number,
          reviewers: [suggestedReviewer]
        });
      }
```

### Add Labels on Claim

Automatically add "in-review" label:

```yaml
- name: Add Label
  uses: actions/github-script@v7
  with:
    script: |
      await github.rest.issues.addLabels({
        owner: context.repo.owner,
        repo: context.repo.repo,
        issue_number: context.issue.number,
        labels: ['in-review', '👀-claimed']
      });
```

### Track Review Time

Add timestamp to track how long reviews take:

```yaml
- name: Add Timestamp Comment
  uses: actions/github-script@v7
  with:
    script: |
      const now = new Date().toISOString();
      await github.rest.issues.createComment({
        owner: context.repo.owner,
        repo: context.repo.repo,
        issue_number: context.issue.number,
        body: `⏱️ Review claimed at ${now}`
      });
```

## Multiple Reviewers

To allow multiple people to claim:

```yaml
- name: Check Multiple Claims
  uses: actions/github-script@v7
  with:
    script: |
      const { data: comments } = await github.rest.issues.listComments({
        owner: context.repo.owner,
        repo: context.repo.repo,
        issue_number: context.issue.number
      });
      
      const claimers = comments
        .filter(c => c.body.includes('/claim') || c.body.includes('👀'))
        .map(c => c.user.login);
      
      // Request all claimers as reviewers
      if (claimers.length > 0) {
        await github.rest.pulls.requestReviewers({
          owner: context.repo.owner,
          repo: context.repo.repo,
          pull_number: context.issue.number,
          reviewers: [...new Set(claimers)] // Remove duplicates
        });
      }
```

## Comparison: Serverless vs Webhook Server

| Feature | Serverless (This Approach) | Webhook Server |
|---------|---------------------------|----------------|
| **Setup** | ⚡ 5 minutes | 🔧 30+ minutes |
| **Infrastructure** | ✅ None needed | ❌ Need hosting |
| **Cost** | 💰 Free | 💰 $0-5/month |
| **Maintenance** | ✅ Zero | ⚠️ Updates needed |
| **Slack Reactions** | ❌ Not supported | ✅ Supported |
| **PR Comments** | ✅ Supported | ✅ Supported |
| **Reliability** | ✅ GitHub SLA | ⚠️ Depends on host |
| **Complexity** | ✅ Simple | ❌ Complex |

## Why This Approach is Better

1. **No Server = No Problems**
   - No hosting costs
   - No server maintenance
   - No downtime worries

2. **GitHub Native**
   - Uses GitHub's infrastructure
   - Better integration with PR workflow
   - Visible in PR timeline

3. **Transparent**
   - Team sees who claimed review in PR comments
   - Creates audit trail
   - Easy to track in PR history

4. **Simple Setup**
   - Just commit workflow files
   - No external services to configure
   - Works immediately

## Limitations

- ❌ Cannot detect Slack emoji reactions (requires webhook server)
- ✅ Users must visit GitHub PR to claim (good for accountability!)
- ✅ Requires one extra step (commenting)

## Alternative: Slack Shortcuts

If you want Slack integration without a server, consider using Slack Workflow Builder:

1. Create Slack Workflow with shortcut
2. Prompt user for PR number
3. Opens PR URL in browser
4. User comments `/claim`

This is still simpler than running a webhook server!

## Troubleshooting

### Workflow not triggering

- Verify Actions are enabled (Settings → Actions)
- Check workflow file is in `.github/workflows/`
- Look for errors in Actions tab

### Not added as reviewer

- Ensure you have write access to repository
- Check if PR is from a fork (has limitations)
- Verify GitHub token permissions

### Slack notification not posting

- Check `SLACK_WEBHOOK_URL` secret is set
- Verify webhook URL is valid
- Look at workflow logs for errors

### Comment not recognized

- Use exact keywords: `/claim` or `👀`
- Check for typos or extra spaces
- Try just the keyword alone in comment

## Cost

**100% FREE** ✅

- GitHub Actions: Free for public repos, 2000 min/month for private
- Each workflow run: ~10-20 seconds
- No hosting or infrastructure costs

## Next Steps

1. ✅ Workflows are already set up
2. 🧪 Test by commenting `/claim` on a PR
3. 📊 Monitor in Actions tab
4. 🎨 Customize keywords and messages as needed
5. 📢 Tell your team about the new feature!

---

**No servers. No complexity. Just GitHub Actions magic.** ✨

