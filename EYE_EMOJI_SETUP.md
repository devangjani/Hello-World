# Slack Eye Emoji Reaction Setup 👀

> **Note:** This is for Option 2 (reacting with 👀 emoji in Slack). For simpler setup, see [Quick Start in README](README.md#option-1-basic-setup-recommended).

Set up eye emoji reactions so team members can claim PR reviews directly from Slack messages by reacting with 👀.

## What You Get

✅ React with 👀 emoji on Slack PR notifications  
✅ Message added to PR: "Getting reviewed by @yourname"  
✅ You're added as reviewer on GitHub  
✅ Confirmation posted in Slack thread  

## Flow

```
Slack message with PR
    ↓
User reacts with 👀
    ↓
Webhook server detects reaction
    ↓
Triggers GitHub Actions
    ↓
Adds "Getting reviewed by @user" to PR
Assigns user as reviewer
    ↓
Confirms in Slack thread
```

## Prerequisites

- ✅ Completed [basic setup](README.md#option-1-basic-setup-recommended)
- ⏱️ 15 additional minutes
- 🚀 Free hosting account (Heroku, Railway, or Vercel)

---

## Setup Steps

### Part 1: Upgrade Slack App

#### 1. Add Bot Token Scopes

1. Go to [api.slack.com/apps](https://api.slack.com/apps)
2. Select your "PR Review Bot" app
3. Click **"OAuth & Permissions"** in sidebar
4. Scroll to **"Bot Token Scopes"**
5. Add these scopes:
   - `chat:write` - Post messages
   - `reactions:read` - Read emoji reactions
   - `users:read` - Get user information
   - `users:read.email` - Get user emails (for GitHub mapping)
   - `channels:history` - Read channel messages
   - `groups:history` - Read private channel messages

#### 2. Reinstall App

1. Scroll up to **"OAuth Tokens for Your Workspace"**
2. Click **"Reinstall to Workspace"**
3. Review new permissions and click **"Allow"**
4. **Copy the "Bot User OAuth Token"** (starts with `xoxb-`)
5. Save this - you'll need it for deployment

#### 3. Get Signing Secret

1. Click **"Basic Information"** in sidebar
2. Scroll to **"App Credentials"**
3. **Copy the "Signing Secret"**
4. Save this as well

### Part 2: Deploy Webhook Server

The webhook server listens for Slack reactions and triggers GitHub Actions. Choose your preferred hosting:

#### Option A: Deploy to Heroku (Recommended)

**Why Heroku:** Simple, free tier available, reliable

1. **Install Heroku CLI:**
   ```bash
   # Mac
   brew install heroku
   
   # Or download from heroku.com
   ```

2. **Login:**
   ```bash
   heroku login
   ```

3. **Create Heroku app:**
   ```bash
   heroku create your-pr-bot-name
   ```

4. **Set environment variables:**
   ```bash
   heroku config:set SLACK_SIGNING_SECRET=your_signing_secret_here
   heroku config:set SLACK_BOT_TOKEN=xoxb-your-bot-token-here
   heroku config:set GITHUB_TOKEN=your_github_token_here
   heroku config:set GITHUB_REPO_OWNER=your-github-username
   heroku config:set GITHUB_REPO_NAME=your-repo-name
   ```

5. **Deploy:**
   ```bash
   git add .
   git commit -m "Add Slack webhook server"
   git push heroku main
   ```

6. **Your webhook URL:** `https://your-pr-bot-name.herokuapp.com/slack/events`

#### Option B: Deploy to Railway.app

**Why Railway:** Even simpler than Heroku, modern dashboard

1. Go to [railway.app](https://railway.app)
2. Sign in with GitHub
3. Click **"New Project"**
4. Select **"Deploy from GitHub repo"**
5. Choose your Hello-World repository
6. Railway will detect `package.json` and deploy automatically
7. Click **"Variables"** tab and add:
   - `SLACK_SIGNING_SECRET`
   - `SLACK_BOT_TOKEN`
   - `GITHUB_TOKEN`
   - `GITHUB_REPO_OWNER`
   - `GITHUB_REPO_NAME`
8. Click **"Settings"** → Copy your public URL
9. Your webhook URL: `https://your-app.up.railway.app/slack/events`

#### Option C: Deploy to Vercel

**Why Vercel:** Great for serverless, free tier

1. **Install Vercel CLI:**
   ```bash
   npm i -g vercel
   ```

2. **Create `vercel.json`:**
   ```json
   {
     "version": 2,
     "builds": [{ "src": "slack-event-handler.js", "use": "@vercel/node" }],
     "routes": [{ "src": "/(.*)", "dest": "slack-event-handler.js" }],
     "env": {
       "SLACK_SIGNING_SECRET": "@slack-signing-secret",
       "SLACK_BOT_TOKEN": "@slack-bot-token",
       "GITHUB_TOKEN": "@github-token",
       "GITHUB_REPO_OWNER": "@github-repo-owner",
       "GITHUB_REPO_NAME": "@github-repo-name"
     }
   }
   ```

3. **Deploy:**
   ```bash
   vercel
   ```

4. **Add secrets in Vercel dashboard**

5. Your webhook URL: `https://your-project.vercel.app/slack/events`

### Part 3: Configure Slack Events

1. Go back to [api.slack.com/apps](https://api.slack.com/apps)
2. Select your app
3. Click **"Event Subscriptions"** in sidebar
4. Toggle **"Enable Events"** to **ON**
5. **Request URL**: Enter your webhook URL
   - Example: `https://your-pr-bot.herokuapp.com/slack/events`
   - Wait for **"Verified ✓"** checkmark (may take a few seconds)
6. Scroll to **"Subscribe to bot events"**
7. Click **"Add Bot User Event"**
8. Add: `reaction_added`
9. Click **"Save Changes"**
10. Slack will prompt you to **reinstall the app** - do it!

### Part 4: Add GitHub Secret

1. Go to your GitHub repository
2. **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"**
4. Name: `SLACK_BOT_TOKEN`
5. Value: Your bot token (xoxb-...)
6. Click **"Add secret"**

### Part 5: Test!

1. **Trigger PR notification:**
   - Go to **Actions** tab
   - Run "PR Review Slack Notification" workflow
   - Check Slack for PR message

2. **React with 👀 emoji:**
   - Click the 👀 emoji on the Slack message

3. **Watch the magic:**
   - Check your webhook server logs (Heroku/Railway dashboard)
   - Should see: "Eye emoji reaction detected!"
   - Check **GitHub Actions** - "Handle Slack Eye Emoji Reaction" workflow runs
   - Check **PR on GitHub** - Comment appears: "Getting reviewed by @you"
   - You're added as reviewer
   - Check **Slack** - Confirmation in thread: "✅ @you is now reviewing PR #42"

---

## User Mapping (Slack to GitHub)

The bot automatically maps Slack users to GitHub users by email. For best results:

### Ensure Emails Match

Team members should use the same email for:
- Slack profile
- GitHub account

The bot will find GitHub users automatically!

### Manual Mapping (Optional)

If emails don't match, add manual mappings in `.github/workflows/handle-slack-reaction.yml`:

```yaml
- name: Map Slack to GitHub User
  id: map-user
  uses: actions/github-script@v7
  with:
    script: |
      const slackUserId = '${{ github.event.client_payload.user_id }}';
      
      // Manual mapping: Slack User ID → GitHub username
      const userMap = {
        'U01ABC123': 'github-username-1',
        'U02DEF456': 'github-username-2',
        'U03GHI789': 'github-username-3'
      };
      
      const githubUsername = userMap[slackUserId];
      const slackName = ${{ steps.slack-user.outputs.result }}.slackName;
      
      return { githubUsername, slackName };
```

**To get Slack User IDs:**
- Right-click user in Slack → **View profile** → **⋯ More** → **Copy member ID**

---

## Troubleshooting

### "Request URL" not verifying

- ✅ Ensure server is running and publicly accessible
- ✅ Try accessing `https://your-url/health` in browser (should show `{"status":"ok"}`)
- ✅ Check server logs for errors
- ✅ Make sure URL ends with `/slack/events`

### Reactions not triggering workflow

- ✅ Check webhook server logs - should see "Eye emoji reaction detected"
- ✅ Verify `reaction_added` event is subscribed in Slack
- ✅ Ensure app is reinstalled after adding event subscription
- ✅ Check PR number is being extracted from message

### User not added as reviewer

- ✅ Verify email mapping is working (check logs)
- ✅ Ensure GitHub token has correct permissions
- ✅ Check user has write access to repository
- ✅ Look at GitHub Actions workflow logs for errors

### Slack confirmation not posting

- ✅ Verify `SLACK_BOT_TOKEN` secret is set in GitHub
- ✅ Ensure bot token hasn't expired
- ✅ Check bot has `chat:write` scope
- ✅ Verify bot is invited to the channel

---

## Cost

**Total: $0/month** 🎉

- **Heroku**: Free tier (sleeps after 30 min inactivity, wakes on request)
- **Railway**: $5 free credit monthly
- **Vercel**: Free serverless tier
- **GitHub Actions**: Free for public repos, 2000 min/month for private

The webhook server uses minimal resources - well within free tiers.

---

## Advanced Customization

### Support Multiple Reactions

Edit `slack-event-handler.js`:

```javascript
if (event.type === 'reaction_added') {
  const reactionMap = {
    'eyes': 'review',
    'white_check_mark': 'approve',
    'x': 'request-changes'
  };
  
  const action = reactionMap[event.reaction];
  if (action) {
    // Handle accordingly
  }
}
```

### Auto-assign Based on Code Ownership

Add logic to suggest reviewers based on changed files:

```javascript
const codeOwners = {
  'frontend/': ['frontend-lead'],
  'backend/': ['backend-lead'],
  'docs/': ['tech-writer']
};
```

### Add Custom Notifications

Post to different Slack channels based on PR labels or files changed.

---

## Security

🔒 **Important:**

- Never commit `.env` files or tokens to Git
- Use environment variables for all secrets
- Verify Slack request signatures (already implemented)
- Rotate tokens periodically
- Use HTTPS endpoints only
- Restrict GitHub token to minimum required permissions

---

## Comparison with Serverless Approach

| Feature | This (Slack Reactions) | Serverless (Comments) |
|---------|----------------------|---------------------|
| **Where to claim** | Slack (emoji) | GitHub (comment) |
| **Setup complexity** | Medium (15 min) | Easy (5 min) |
| **Infrastructure** | Small server | None |
| **User experience** | ⭐⭐⭐⭐⭐ Sleek | ⭐⭐⭐⭐ Good |
| **Maintenance** | Low | None |
| **Result** | Same! | Same! |

Both add "Getting reviewed by @user" and assign reviewer. Only difference is where you click!

---

## Need Help?

- Check webhook server logs (Heroku logs, Railway logs, etc.)
- Check GitHub Actions workflow logs
- Verify all environment variables are set
- Test webhook URL with: `curl https://your-url/health`

---

**Ready to use?** React with 👀 on any PR notification in Slack and watch the automation work!

[← Back to Main README](README.md)
