# Telegram Keyword Forwarding Bot

A Telegram bot that forwards messages from groups to users based on configured keywords. Built with Python, aiogram v3, and SQLite. Deployed on Render.

## Features

- **Per-group, per-user keywords**: Different users can configure different keywords in the same group
- **Keyword matching**: Case-insensitive, regex-safe matching with word boundaries (prevents partial matches)
- **Optional regex mode**: Users can add regex patterns as keywords
- **Private message forwarding**: Matched messages are forwarded to keyword owners with context
- **Cooldown protection**: Prevents duplicate forwards (default 30 seconds)
- **SQLite persistence**: Lightweight database storage
- **Polling mode**: No webhooks required, works reliably on Render

## How It Works

1. Add the bot to a Telegram group
2. Disable bot privacy mode via BotFather (`/setprivacy -> Disable`)
3. Add keywords via private chat: `/add "Group Name" keyword1 keyword2`
4. When a message in the group contains a keyword, the bot forwards it to the keyword owner

## Bot Commands

- `/start` - Welcome and usage instructions
- `/help` - Detailed help for all commands
- `/add "Group Name" keyword1 keyword2` - Add keywords for a group (from private chat)
- `/remove keyword` - Remove a keyword
- `/list` - List all your keywords
- `/clear` - Clear all keywords for current group

## Local Development

### Prerequisites

- Python 3.11+
- Telegram Bot Token from BotFather

### Setup

```bash
# Clone repository
git clone https://github.com/yourusername/telegrambot.git
cd telegrambot

# Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and set BOT_TOKEN=your_token_here

# Run bot locally
python main.py
```

## Deploy on Render

### Prerequisites

- GitHub account with repository pushed
- Render.com account (free tier available)
- Telegram Bot Token

### Step-by-Step Deployment

#### 1. Push to GitHub

```bash
git add .
git commit -m "Deploy to Render"
git push origin main
```

#### 2. Deploy on Render

1. Visit https://render.com
2. Click **Dashboard** (sign in/create account)
3. Click **New +** → **Blueprint**
4. Connect your GitHub repository
5. Select this repository from the dropdown
6. Render will automatically detect `render.yaml`
7. Click **Create New Services**

Render will:
- Detect the `render.yaml` configuration
- Create a **Worker** service (not web service)
- Build the application
- Deploy the bot

#### 3. Configure Environment Variables

1. In Render Dashboard, go to your **Worker** service
2. Click **Environment** tab
3. Add a new environment variable:
   - **Key**: `BOT_TOKEN`
   - **Value**: `your_bot_token_here`
4. Click **Save Changes**

The service will automatically restart with the new variable.

#### 4. Monitor

- Go to **Logs** tab to see real-time bot output
- Look for message: `Starting bot polling`
- Verify no error messages in logs

### Testing

1. Add the bot to a test Telegram group
2. Send a message in the group (so bot records group title)
3. In private chat, add a keyword: `/add "Test Group" hello`
4. Send a message in the group containing "hello"
5. Bot should forward the message to you privately

### Making Updates

To update the bot:

```bash
# Make code changes locally
nano app/handlers/messages.py  # for example

# Push to GitHub
git add .
git commit -m "Update bot logic"
git push origin main
```

Render will automatically detect the push and redeploy.

### Manual Restart

To restart the bot without redeploying:

1. Go to Render Dashboard → Your Worker service
2. Click **More** (three dots) → **Manual Deploy** or **Restart**
3. Service will restart immediately

## Environment Variables

### Required

- `BOT_TOKEN` - Your Telegram bot token from BotFather

### Optional

- `LOG_LEVEL` - Logging level: `DEBUG`, `INFO` (default), `WARNING`, `ERROR`
- `COOLDOWN_SECONDS` - Cooldown between duplicate forwards (default: 30)
- `SQLITE_PATH` - Path to database file (default: `./data/bot.db`)

## Database & Persistence

SQLite database is stored in `./data/bot.db` and persists on Render's ephemeral disk.

### Important Notes

- **Render Free Tier**: Disk is ephemeral and may be reset periodically
- **Database Survival**: Your database will survive between restarts but may be lost if the service is deleted
- **Backup Recommendations**: For production use, consider:
  - Periodic manual backups by downloading the database
  - Migrating to PostgreSQL (Render offers free PostgreSQL)
  - Using an external database service

### Accessing the Database

Unfortunately, Render doesn't provide easy database download for free tier services. To preserve your keywords:

1. Manually add keywords to your personal list
2. Or migrate to PostgreSQL (contact Render support for guidance)

## Logs & Monitoring

### Viewing Logs

In Render Dashboard:

1. Go to your **Worker** service
2. Click **Logs** tab
3. View real-time bot output

### Log Levels

Control verbosity by setting `LOG_LEVEL` environment variable:

- `DEBUG` - Very detailed (includes all matches)
- `INFO` - Normal (recommended, shows matched keywords and forwards)
- `WARNING` - Important issues only
- `ERROR` - Critical errors only

### Important Log Messages

- `Starting bot polling` - Bot is running and listening
- `Matched keyword:` - A keyword was found in a message
- `Forwarded message` - Successfully forwarded to user
- Error messages - Indicate issues to troubleshoot

## Troubleshooting

### Bot not forwarding messages

1. **Check privacy mode**: Use BotFather `/setprivacy -> Disable` for the bot
2. **Group not recorded**: Send a message in the group so bot records the group title
3. **Exact group name match**: When using `/add`, group name must match exactly
4. **Check logs**: View Render logs for error messages

### Bot not starting

1. Check `BOT_TOKEN` is set in Render environment variables
2. Review logs for specific error message
3. Restart the service: Dashboard → More → **Manual Deploy**
4. Check if BOT_TOKEN format is correct (long string)

### Bot not responding to commands

1. Verify BOT_TOKEN is correct
2. Check Render logs for errors
3. Ensure bot was added to groups you're testing in
4. Try `/help` command first

### Deployment failed

1. Check GitHub repository is public
2. Verify `render.yaml` exists at project root
3. Check `requirements.txt` has all dependencies
4. Review Render build logs for specific errors

### Database errors

1. Check available disk space in logs
2. If database is corrupted, delete `data/bot.db` and restart (keywords will be lost)
3. Consider using PostgreSQL for production (more reliable)

## Limitations of Render Free Tier

- **Ephemeral Disk**: Disk may be reset, but typically survives restarts
- **CPU/Memory**: Shared resources (sufficient for this polling bot)
- **Build Time**: Limited free build minutes per month
- **Inactivity**: Service may be paused after inactivity (Render may update this policy)

Check Render's current free tier terms at https://render.com/pricing.

## File Structure

```
.
├── app/
│   ├── handlers/          # Command and message handlers
│   ├── services/          # Business logic (matcher, cooldown, forwarding)
│   ├── database/          # SQLite models and queries
│   ├── utils/             # Logging and helpers
│   └── config.py          # Configuration from environment
├── main.py                # Bot entry point
├── render.yaml            # Render Blueprint configuration
├── requirements.txt       # Python dependencies
├── .env.example           # Example environment variables
├── README.md              # This file
└── .gitignore             # Git ignore rules
```

## Frequently Asked Questions

### Can I use webhooks instead of polling?

No, this bot uses polling mode for simplicity and reliability. Webhooks would require a web server, which is unnecessary for this use case.

### Can I use PostgreSQL instead of SQLite?

Yes! PostgreSQL can be set up on Render (free tier available). However, this would require code changes to replace SQLite. Open an issue if you need guidance.

### Will my keywords be lost if Render resets the disk?

Possibly. Render's free tier uses ephemeral storage. Keywords survive normal restarts but may be lost during infrastructure maintenance. For production, consider PostgreSQL or regular backups.

### Can I run this on a paid plan?

Yes! Upgrading to a paid Render plan will give you:
- Persistent storage (paid disk)
- Better resource allocation
- Priority support

### How do I migrate from other platforms?

If you previously ran this on another platform:
- The bot logic is identical, only deployment changed
- Just push to GitHub and deploy using the Render steps above
- Your database will be fresh on Render (configure keywords again)

## Support

For issues:

1. Check the **Troubleshooting** section above
2. Review bot logs in Render Dashboard
3. Check `/help` command in Telegram for bot usage
4. Review source code in `app/` directory

For Render-specific issues:
- Render Docs: https://render.com/docs
- Render Status: https://status.render.com

For Telegram Bot API issues:
- Telegram Bot API: https://core.telegram.org/bots
- aiogram v3: https://docs.aiogram.dev/

## License

MIT
"# telegram" 
