# Render Deployment Guide

This guide describes how to deploy the Telegram keyword-forwarding bot on Render as a background Worker using polling mode.

Prerequisites
- GitHub repository containing the bot code
- Render account (free tier sufficient)
- Telegram Bot Token (BOT_TOKEN) from BotFather

1) Prepare the repository
- Ensure the repository has render.yaml at the repo root (Render will auto-detect)
- Push code to GitHub: git push origin main

2) Render setup
- In Render, create a new Native or GitHub-linked project from the repository
- Choose a Worker service (not Web Service)
- Render will auto-detect render.yaml; confirm the settings
- Set environment variable BOT_TOKEN (and optionally LOG_LEVEL, COOLDOWN_SECONDS, SQLITE_PATH)
- Start deployment

3) Logs & verification
- Open the Render project -> Logs to monitor startup
- Look for the line: Starting bot polling
- Test by adding the bot to a group (disable privacy mode) and using /add in private chat

4) Operational notes
- The bot uses polling mode; no web server ports are opened
- The SQLite database is stored in ./data/bot.db within the repo
- Free tier may have ephemeral disk; consider a cloud DB if you scale

5) Restarting
- Use Render dashboard -> Worker service -> Restart
- Or push a new commit to trigger redeploy

6) Rollback / Troubleshooting
- If deployment fails, check GitHub Actions or Render build logs
- Ensure BOT_TOKEN is valid and has permissions in BotFather privacy mode is disabled
- Review logs for errors related to bot initialization or API calls
