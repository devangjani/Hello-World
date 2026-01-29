# Serverless Slack Emoji Setup (Poll-Based) 👀

This approach lets you use Slack emoji reactions WITHOUT a webhook server by having GitHub Actions periodically check Slack for new reactions.

## How It Works

```
GitHub Actions (runs every 1 min)
    ↓
Polls Slack API for messages
    ↓
Finds messages with 👀 reactions
    ↓
Extracts PR number from message
    ↓
Adds comment: "Getting reviewed by @user"
    ↓
Assigns reviewer on GitHub
    ↓
Removes reaction (marks as processed)
```

**Delay:** Up to 1 minute (nearly instant!)

---

## Setup (10 Minutes)

### Step 1: Create Slack Bot Token

1. Go to [api.slack.com/apps](https://api.slack.com/apps)
2. Click your "PR Review Bot" app (or create new)
3. **OAuth & Permissions** → **Bot Token Scopes**, add:
   - `channels:history` - Read messages
   - `groups:history` - Read private channels
   - `reactions:read` - Read reactions
   - `reactions:write` - Remove reactions (optional)
   - `users:read` - Get user info
   - `users:read.email` - Match users to GitHub

4. **Install App to Workspace** (or reinstall if already installed)
5. Copy **Bot User OAuth Token** (starts with `xoxb-`)

### Step 2: Get Slack Channel ID

**Method 1: From Slack**
- Right-click your channel → **View channel details**
- Scroll down to find **Channel ID**
- Copy it (looks like: `C01ABC123DE`)

**Method 2: From URL**
- Open your Slack channel in browser
- URL will be: `https://app.slack.com/client/T.../C01ABC123DE`
- The `C01ABC123DE` part is your channel ID

### Step 3: Add GitHub Secrets

1. Go to GitHub repo → **Settings** → **Secrets and variables** → **Actions**
2. Add two secrets:

**Secret 1:**
- Name: `SLACK_BOT_TOKEN`
- Value: `xoxb-your-bot-token-here`

**Secret 2:**
- Name: `SLACK_CHANNEL_ID`  
- Value: `C01ABC123DE` (your channel ID)

### Step 4: Push the Workflow

The workflow is already created at `.github/workflows/poll-slack-reactions.yml`

Commit and push:
```bash
cd "/Users/devangj/Documents/My Data/git/Hello-World"
git add .github/workflows/poll-slack-reactions.yml
git commit -m "Add polling-based Slack emoji reaction handler"
git push origin master
```

### Step 5: Test!

1. **Trigger PR notification** (existing workflow)
2. **React with 👀** on the Slack message
3. **Wait up to 1 minute** (or manually trigger workflow)
4. **Check PR** - should see comment and reviewer assigned
5. **Check Actions** tab - see "Poll Slack for Eye Emoji Reactions" running

---

## Configuration

### Change Polling Frequency

Edit `.github/workflows/poll-slack-reactions.yml`:

```yaml
on:
  schedule:
    - cron: '*/1 * * * *'   # Every 1 minute (current)
    # - cron: '*/2 * * * *'  # Every 2 minutes
    # - cron: '*/5 * * * *'  # Every 5 minutes (less frequent)
```

**Note:** More frequent = more Actions minutes used (still well within free tier)

### Keep Reactions Visible

If you don't want reactions removed after processing, comment out this section in the workflow:

```yaml
# Optional: Remove the reaction to mark as processed
# try {
#   await fetch(...)
# } catch (error) {
#   console.log('⚠️ Could not remove reaction');
# }
```

### Manual User Mapping

If email matching doesn't work, add manual mappings:

```javascript
// Manual mapping: Slack User ID → GitHub username
const userMap = {
  'U01ABC123': 'github-user-1',
  'U02DEF456': 'github-user-2'
};

let githubUsername = userMap[userId];
if (!githubUsername && slackEmail) {
  // Fall back to email search
  // ... existing code ...
}
```

---

## Comparison

| Feature | Poll-Based (This) | Webhook Server | Comment-Based |
|---------|------------------|----------------|---------------|
| **Claim method** | 👀 in Slack | 👀 in Slack | `/claim` on GitHub |
| **Response time** | ~1 minute | Instant | Instant |
| **Infrastructure** | None | Server needed | None |
| **Setup time** | 10 min | 20 min | 5 min |
| **Maintenance** | Zero | Updates needed | Zero |
| **Cost** | Free | Free* | Free |
| **Complexity** | Low | High | Very Low |

\* Requires free hosting

---

## Advantages Over Webhook Server

✅ **No server to maintain** - Runs entirely in GitHub Actions  
✅ **No hosting needed** - No Heroku, Railway, or Vercel  
✅ **No downtime** - GitHub's infrastructure  
✅ **Simple setup** - Just add two secrets  
✅ **Still supports Slack emojis** - Team stays in Slack  

## Trade-offs

⏱️ **Minimal delay** - Up to 1 minute vs instant  
📊 **GitHub Actions usage** - ~60 runs/hour (still well within free tier)  

---

## Cost Analysis

**GitHub Actions usage:**
- 60 runs per hour × 24 hours = 1,440 runs/day
- Each run: ~30 seconds
- Daily usage: 1,440 × 0.5 = 720 minutes/day
- Monthly: ~21,600 minutes

**Free tier for private repos:** 2,000 minutes/month

**Important:** This exceeds free tier for private repos! Consider:
- Use public repo (unlimited free)
- Reduce to every 2-3 minutes
- Upgrade GitHub plan if needed

**For public repos:** Completely free, unlimited minutes! ✅

For public repos: Completely free, unlimited.

---

## Troubleshooting

### Workflow not running

- Check Actions are enabled
- Verify cron schedule syntax
- Manually trigger via Actions tab → "Run workflow"

### No reactions detected

- Verify `SLACK_BOT_TOKEN` is correct
- Check `SLACK_CHANNEL_ID` is correct
- Ensure bot is invited to the channel: `/invite @PR Review Bot`
- Check bot has required scopes

### Users not mapped to GitHub

- Verify users use same email in Slack and GitHub
- Add manual mapping (see Configuration section)
- Check `users:read.email` scope is enabled

### Reactions not removed

- Needs `reactions:write` scope
- Bot must be in the channel
- Optional feature - can be disabled

---

## Recommendation

**This poll-based approach is ideal if:**
- ✅ You want Slack emoji reactions
- ✅ 2-5 minute delay is acceptable
- ✅ You don't want to maintain a server
- ✅ Team prefers staying in Slack

**Use comment-based if:**
- ✅ You need instant response
- ✅ Team is comfortable with GitHub
- ✅ You want the absolute simplest setup

---

**Ready to test?** Add the secrets and watch it work automatically!
