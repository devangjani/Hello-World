# GitHub PR Review Bot 🤖

A bot that automatically fetches open GitHub Pull Requests awaiting review and posts them to Slack with beautiful formatting, plus the ability for team members to claim reviews.

## 🎯 Features

### 📊 Automated PR Notifications
- 🔍 Fetches all open PRs from your GitHub repository
- 🎯 Filters PRs that need review (excludes drafts, shows unreviewed PRs)
- 📊 Beautiful Slack formatting with priority indicators
- 🎨 Color-coded by age (🟢 new, 🟡 3+ days, 🔴 7+ days)
- 👥 Shows assigned reviewers and author information
- 🏷️ Displays PR labels
- ⏰ Shows how long each PR has been open
- 🔄 Runs automatically on schedule or on PR events

### 👀 Review Claiming - Two Options

**Option 1: Serverless (Easy Setup)** ⭐ Recommended
- 💬 Comment `/claim` or `👀` on GitHub PR
- ✅ Auto-assigns reviewer + adds message: "Getting reviewed by @username"
- **No server required!**

**Option 2: Slack Emoji Reactions (Full Integration)**
- 👀 React with eye emoji directly on Slack message
- ✅ Auto-assigns reviewer + adds message: "Getting reviewed by @username"
- ⚠️ Requires small webhook server (free hosting available)

👉 **[Not sure which to choose? See comparison](CHOOSE_SETUP.md)**

---

## 🚀 Quick Start (5 Minutes)

### Choose Your Setup

**🟢 Option 1: Basic Setup (Notifications Only)**
- ✅ PR notifications in Slack
- ✅ Comment `/claim` on GitHub to claim reviews
- ⏱️ 5 minute setup

**🔵 Option 2: Full Setup (Slack Emoji Reactions)**
- ✅ All features from Option 1
- ✅ React with 👀 emoji directly in Slack
- ⏱️ 15 minute setup (requires webhook server)

---

## 📝 Setup Instructions

### Option 1: Basic Setup (Recommended)

#### Step 1: Create Slack Incoming Webhook

1. Go to [Slack API Apps](https://api.slack.com/apps)
2. Click **"Create New App"** → **"From scratch"**
3. Name: "PR Review Bot", select workspace
4. Go to **"Incoming Webhooks"** → Toggle ON
5. **"Add New Webhook to Workspace"** → Select channel
6. **Copy the webhook URL**

#### Step 2: Add to GitHub Secrets

1. Repository → **Settings** → **Secrets and variables** → **Actions**
2. **"New repository secret"**
3. Name: `SLACK_WEBHOOK_URL`
4. Value: Paste webhook URL
5. **"Add secret"**

#### Step 3: Enable Workflows

1. Go to **Actions** tab
2. Enable Actions if needed
3. Workflows will appear automatically

#### Step 4: Test!

**Test Notifications:**
- Actions tab → "PR Review Slack Notification" → "Run workflow"
- Check Slack for PR notifications

**Test Claiming:**
- Open any PR → Comment `/claim` or `👀`
- You'll be assigned as reviewer with message: "Getting reviewed by @yourname"

✅ **Done! You're all set.**

---

### Option 2: Full Slack Integration

Want to react with 👀 emoji directly on Slack messages? Follow these additional steps:

#### Additional Requirements
- Slack Bot Token (we'll create this)
- Small Node.js server (free hosting options provided)

#### Setup Steps

**1. Upgrade Slack App**
- Go to your Slack app at [api.slack.com/apps](https://api.slack.com/apps)
- **"OAuth & Permissions"** → Add Bot Token Scopes:
  - `chat:write`
  - `reactions:read`
  - `users:read`
  - `users:read.email`
  - `channels:history`
  - `groups:history`
- **"Reinstall App"** to workspace
- Copy **Bot User OAuth Token** (starts with `xoxb-`)

**2. Deploy Webhook Server**

Choose a free hosting option:

**Heroku (Easiest):**
```bash
# Install Heroku CLI
brew install heroku  # Mac

# Deploy
heroku create your-pr-bot
heroku config:set SLACK_SIGNING_SECRET=your_signing_secret
heroku config:set SLACK_BOT_TOKEN=xoxb-your-token
heroku config:set GITHUB_TOKEN=your_github_token
heroku config:set GITHUB_REPO_OWNER=your-username
heroku config:set GITHUB_REPO_NAME=your-repo
git push heroku main
```

**Railway.app (Simplest):**
1. Go to [railway.app](https://railway.app)
2. "New Project" → "Deploy from GitHub"
3. Select this repository
4. Add environment variables in dashboard
5. Copy provided URL

**3. Configure Slack Events**
- Slack app → **"Event Subscriptions"** → Toggle ON
- **Request URL**: `https://your-server-url/slack/events`
- Wait for "Verified ✓"
- **Subscribe to bot events**: `reaction_added`
- **Save Changes** → Reinstall app

**4. Add GitHub Secret**
- GitHub → Settings → Secrets → Actions
- Add: `SLACK_BOT_TOKEN` with your bot token

**5. Test Emoji Reactions!**
- PR notification appears in Slack
- React with 👀 emoji
- User is assigned + message added: "Getting reviewed by @user"
- Confirmation posted to Slack thread

📖 **[Detailed Setup Guide](EYE_EMOJI_SETUP.md)**

---

## 📖 How It Works

### PR Notifications

```
GitHub Actions (scheduled/triggered)
    ↓
Fetch open PRs via GitHub API
    ↓
Filter drafts & check review status
    ↓
Format beautiful Slack message
    ↓
Post to Slack channel
```

**Triggers:**
- ⏰ Scheduled: Every hour during work hours (customizable)
- 🆕 New PR opened
- ✅ Draft PR marked as ready for review

### Review Claiming

```
User comments `/claim` on PR
    ↓
GitHub Actions detects comment
    ↓
Assigns user as reviewer
    ↓
Adds status comment to PR
    ↓
Reacts to claim comment
    ↓
Notifies Slack (optional)
```

**Supported claim keywords:**
- `/claim`
- `👀` (just the emoji)
- `/review`
- `reviewing this`

---

## ⚙️ Configuration

### Customize Schedule

Edit `.github/workflows/pr-review-slack-notification.yml`:

```yaml
on:
  schedule:
    - cron: '0 9-17 * * 1-5'  # Every hour, 9 AM-5 PM UTC, Mon-Fri
```

**Common schedules:**
- Every hour: `'0 * * * *'`
- Every 2 hours: `'0 */2 * * *'`
- Every day at 9 AM: `'0 9 * * *'`
- Twice daily (9 AM & 2 PM): `'0 9,14 * * *'`

Use [crontab.guru](https://crontab.guru/) to create custom schedules.

### Customize Claim Keywords

Edit `.github/workflows/handle-pr-claim.yml` to add your own keywords:

```yaml
const claimKeywords = ['/claim', '👀', '/review', 'reviewing this', 'on it'];
```

### Add Auto-Labels

Automatically label PRs when claimed:

```yaml
- name: Add Label
  uses: actions/github-script@v7
  with:
    script: |
      await github.rest.issues.addLabels({
        owner: context.repo.owner,
        repo: context.repo.repo,
        issue_number: context.issue.number,
        labels: ['in-review']
      });
```

---

## 📨 Slack Message Format

```
📋 Pull Requests Awaiting Review (3)
Repository: `owner/repo`
─────────────────────────────

🟢 #42: Add new feature
👤 Author: johndoe
👥 Reviewers: @reviewer1, @reviewer2
📅 Created: 2 days ago
🏷️ Labels: `feature`, `needs-review`

👀 To claim this review, comment `/claim` or 👀 on the PR
[👀 Review This] ← Button opens PR

─────────────────────────────

🟡 #38: Fix authentication bug
👤 Author: janedoe
👥 Reviewers: No reviewers assigned
📅 Created: 5 days ago

👀 To claim this review, comment `/claim` or 👀 on the PR
[👀 Review This]

─────────────────────────────

Last updated: Jan 29, 2026 10:30 AM
```

---

## 🔧 Troubleshooting

### Workflow not running

- ✅ Check Actions are enabled (Settings → Actions)
- ✅ Verify workflow file is in `.github/workflows/`
- ✅ Check workflow syntax in Actions tab
- ✅ For scheduled runs, may be delayed up to 10 minutes

### Slack messages not appearing

- ✅ Verify `SLACK_WEBHOOK_URL` secret is set
- ✅ Test webhook with curl:
  ```bash
  curl -X POST -H 'Content-type: application/json' \
    --data '{"text":"Test"}' YOUR_WEBHOOK_URL
  ```
- ✅ Check workflow logs for errors

### Claim not working

- ✅ Ensure you have write access to repository
- ✅ Use exact keywords: `/claim` or `👀`
- ✅ Check Actions logs for errors
- ✅ Verify bot has permissions to assign reviewers

### No PRs showing

- ✅ Confirm there are open PRs
- ✅ Check if all PRs are drafts (they're filtered out)
- ✅ Verify workflow has read access

---

## 💰 Cost

**100% FREE** for most teams! ✅

- **Public repositories**: Completely free
- **Private repositories**: 
  - Free tier: 2,000 minutes/month
  - Each run: ~30-60 seconds
  - ~60-120 runs per month = well within free tier
- **SlAdditional Documentation

- **[Serverless Review Claiming](SERVERLESS_SETUP.md)** - Comment-based claiming (no server)
- **[Slack Emoji Setup](EYE_EMOJI_SETUP.md)** - Full Slack integration with reactions
- **[GitHub Actions Config](GITHUB_ACTIONS_SETUP.md)** - Advanced
## 🎨 Advanced Features

### Multiple Repositories

Add the workflows to each repository you want to monitor, or create a central repository that monitors multiple repos.

### Custom Priority Rules

Change age thresholds for priority colors:

```javascript
let priorityEmoji = '🟢';
if (daysOld > 14) priorityEmoji = '🔴';      // 14+ days = red
else if (daysOld > 7) priorityEmoji = '🟡';   // 7+ days = yellow
// Otherwise green
```

### CODEOWNERS Integration

Automatically suggest reviewers based on changed files:

```yaml
- name: Get Suggested Reviewers
  uses: actions/github-script@v7
  with:
    script: |
      const { data: files } = await github.rest.pulls.listFiles({
        owner: context.repo.owner,
        repo: context.repo.repo,
        pull_number: context.issue.number
      });
      
      // Read CODEOWNERS and suggest reviewers
      // Add them automatically or notify them
```

### Prevent Duplicate Claims

Check if PR already has reviewers before allowing claims:

```yaml
- name: Check Existing Reviewers
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
        process.exit(0);
      }
```

---

## 📚 Documentation

- **[Serverless Setup Guide](SERVERLESS_SETUP.md)** - Detailed setup and customization
- **[GitHub Actions Setup](GITHUB_ACTIONS_SETUP.md)** - GitHub Actions configuration

---

## 🐍 Alternative: Python Script

For more flexibility or running outside GitHub Actions, use the Python script:

### Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your tokens
   ```

3. Run manually:
   ```bash
   python pr_review_bot.py
   ```

### When to Use Python Script

- ✅ Need to monitor multiple repositories
- ✅ Want to run on your own schedule/server
- ✅ Need complex custom logic
- ✅ Want more control over the process

---

## 🤝 Contributing

Contributions welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation

---

## 📄 License

This project is open source and available under the MIT License.

---

## 🌟 Why This Bot?

**Problems it solves:**
- 😰 PRs sitting unreviewed for days
- 🤷 Team not aware of pending reviews
- 📧 Email overload from GitHub notifications
- ❓ Unclear who should review what
- 🔄 Manual checking of PR status

**Benefits:**
- ⚡ Instant visibility in Slack
- 🎯 Proactive PR awareness
- 👥 Easy review assignment
- 📊 Priority indicators
- 🤖 Fully automated

---

Made with ❤️ for better PR review workflows

**Questions?** Check the documentation or create an issue!
