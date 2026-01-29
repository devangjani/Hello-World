#!/usr/bin/env python3
"""
GitHub PR Review Bot
Fetches open PRs from GitHub and posts them to Slack channel
"""

import os
import requests
from datetime import datetime
from typing import List, Dict, Optional


class GitHubPRBot:
    """Bot to fetch GitHub PRs and post to Slack"""
    
    def __init__(self, github_token: str, slack_webhook_url: str, github_repo: str):
        """
        Initialize the bot
        
        Args:
            github_token: GitHub Personal Access Token
            slack_webhook_url: Slack Incoming Webhook URL
            github_repo: GitHub repository in format 'owner/repo'
        """
        self.github_token = github_token
        self.slack_webhook_url = slack_webhook_url
        self.github_repo = github_repo
        self.github_api_base = "https://api.github.com"
        
    def fetch_open_prs(self) -> List[Dict]:
        """
        Fetch all open PRs from the GitHub repository
        
        Returns:
            List of PR data dictionaries
        """
        url = f"{self.github_api_base}/repos/{self.github_repo}/pulls"
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        params = {
            "state": "open",
            "sort": "created",
            "direction": "desc"
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching PRs from GitHub: {e}")
            return []
    
    def filter_prs_for_review(self, prs: List[Dict]) -> List[Dict]:
        """
        Filter PRs that need review (not draft, no recent reviews)
        
        Args:
            prs: List of PR data from GitHub API
            
        Returns:
            Filtered list of PRs needing review
        """
        review_needed = []
        
        for pr in prs:
            # Skip draft PRs
            if pr.get('draft', False):
                continue
            
            # Check if PR has requested reviewers
            has_reviewers = (
                len(pr.get('requested_reviewers', [])) > 0 or
                len(pr.get('requested_teams', [])) > 0
            )
            
            # Get review information
            reviews_url = pr.get('url') + '/reviews'
            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            try:
                reviews_response = requests.get(reviews_url, headers=headers)
                reviews_response.raise_for_status()
                reviews = reviews_response.json()
                
                # Check if there are approved reviews
                approved = any(review.get('state') == 'APPROVED' for review in reviews)
                
                # Add PR if it needs review (has reviewers or no approval yet)
                if has_reviewers or not approved:
                    review_needed.append(pr)
                    
            except requests.exceptions.RequestException as e:
                print(f"Error fetching reviews for PR #{pr['number']}: {e}")
                # If we can't fetch reviews, assume it needs review
                review_needed.append(pr)
        
        return review_needed
    
    def format_slack_message(self, prs: List[Dict]) -> Dict:
        """
        Format PRs into a rich Slack message with blocks
        
        Args:
            prs: List of PR data
            
        Returns:
            Slack message payload
        """
        if not prs:
            return {
                "text": "No PRs available for review! 🎉",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "✅ *No PRs available for review!*\n\nAll caught up! 🎉"
                        }
                    }
                ]
            }
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"📋 Pull Requests Awaiting Review ({len(prs)})",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Repository:* `{self.github_repo}`"
                }
            },
            {
                "type": "divider"
            }
        ]
        
        for pr in prs:
            # Parse created date
            created_at = datetime.strptime(pr['created_at'], "%Y-%m-%dT%H:%M:%SZ")
            days_old = (datetime.utcnow() - created_at).days
            age_text = f"{days_old} day{'s' if days_old != 1 else ''} old"
            
            # Build reviewer list
            reviewers = []
            for reviewer in pr.get('requested_reviewers', []):
                reviewers.append(f"@{reviewer['login']}")
            for team in pr.get('requested_teams', []):
                reviewers.append(f"@{team['name']}")
            
            reviewer_text = ", ".join(reviewers) if reviewers else "_No reviewers assigned_"
            
            # Determine priority emoji based on age
            priority_emoji = "🔴" if days_old > 7 else "🟡" if days_old > 3 else "🟢"
            
            # Create PR block
            pr_text = f"{priority_emoji} *<{pr['html_url']}|#{pr['number']}: {pr['title']}>*\n"
            pr_text += f"👤 *Author:* {pr['user']['login']}\n"
            pr_text += f"👥 *Reviewers:* {reviewer_text}\n"
            pr_text += f"📅 *Created:* {age_text}\n"
            
            if pr.get('labels'):
                labels = ", ".join([f"`{label['name']}`" for label in pr['labels']])
                pr_text += f"🏷️ *Labels:* {labels}\n"
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": pr_text
                }
            })
            
            blocks.append({"type": "divider"})
        
        # Add footer
        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"Last updated: <!date^{int(datetime.utcnow().timestamp())}^{{date_num}} {{time_secs}}|{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}>"
                }
            ]
        })
        
        return {
            "text": f"{len(prs)} PR(s) available for review",
            "blocks": blocks
        }
    
    def post_to_slack(self, message: Dict) -> bool:
        """
        Post message to Slack channel
        
        Args:
            message: Slack message payload
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.post(
                self.slack_webhook_url,
                json=message,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            print("✅ Message posted to Slack successfully!")
            return True
        except requests.exceptions.RequestException as e:
            print(f"❌ Error posting to Slack: {e}")
            return False
    
    def run(self, filter_for_review: bool = True):
        """
        Run the bot - fetch PRs and post to Slack
        
        Args:
            filter_for_review: If True, only show PRs that need review
        """
        print(f"🔍 Fetching open PRs from {self.github_repo}...")
        prs = self.fetch_open_prs()
        
        if not prs:
            print("No open PRs found.")
            message = self.format_slack_message([])
            self.post_to_slack(message)
            return
        
        print(f"Found {len(prs)} open PR(s)")
        
        if filter_for_review:
            print("🔎 Filtering PRs that need review...")
            prs = self.filter_prs_for_review(prs)
            print(f"Found {len(prs)} PR(s) needing review")
        
        print("📝 Formatting message for Slack...")
        message = self.format_slack_message(prs)
        
        print("📤 Posting to Slack...")
        self.post_to_slack(message)


def main():
    """Main entry point"""
    # Load configuration from environment variables
    github_token = os.getenv('GITHUB_TOKEN')
    slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    github_repo = os.getenv('GITHUB_REPO')
    
    # Validate configuration
    if not github_token:
        raise ValueError("GITHUB_TOKEN environment variable is required")
    if not slack_webhook_url:
        raise ValueError("SLACK_WEBHOOK_URL environment variable is required")
    if not github_repo:
        raise ValueError("GITHUB_REPO environment variable is required (format: owner/repo)")
    
    # Initialize and run bot
    bot = GitHubPRBot(
        github_token=github_token,
        slack_webhook_url=slack_webhook_url,
        github_repo=github_repo
    )
    
    # Run with filtering (only PRs needing review)
    bot.run(filter_for_review=True)


if __name__ == "__main__":
    main()
