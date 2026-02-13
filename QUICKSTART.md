# Quick Start Guide

Get your GlizzyRaidRoster bot running in 5 minutes!

## Prerequisites

- Python 3.8 or higher installed
- A Discord account with server admin permissions
- 5 minutes of setup time

## Step 1: Clone and Install (1 minute)

```bash
# Clone the repository
git clone https://github.com/gavelinrobert-beep/GlizzyRaidRoster.git
cd GlizzyRaidRoster

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Create Discord Bot (2 minutes)

1. Go to https://discord.com/developers/applications
2. Click "New Application" → Enter a name → Click "Create"
3. Go to "Bot" tab → Click "Add Bot" → Confirm
4. Under "Privileged Gateway Intents", enable:
   - ✅ Server Members Intent
   - ✅ Message Content Intent
5. Click "Reset Token" → Copy the token (you'll need this!)
6. Go to "OAuth2" → "URL Generator"
7. Select scopes: `bot` and `applications.commands`
8. Select permissions: Administrator (or minimal: Send Messages, Embed Links, Use Slash Commands)
9. Copy the URL at the bottom and open it in your browser
10. Select your server and authorize the bot

## Step 3: Get Your Guild ID (30 seconds)

1. In Discord, go to User Settings → Advanced
2. Enable "Developer Mode"
3. Right-click your server icon → "Copy ID"

## Step 4: Configure the Bot (1 minute)

```bash
# Copy the example configuration
cp .env.example .env

# Edit .env with your favorite editor
nano .env  # or vim, code, etc.
```

Update these values in `.env`:
```env
DISCORD_TOKEN=paste_your_bot_token_here
GUILD_ID=paste_your_guild_id_here
```

## Step 5: Start the Bot (30 seconds)

```bash
python bot.py
```

You should see:
```
INFO - Bot is ready! Logged in as YourBotName
INFO - Commands synced to guild XXXXX
```

## Step 6: Test in Discord

In your Discord server, type `/` and you should see the bot's commands appear!

Try:
```
/player_add name:TestPlayer discord_user:@yourself
/roster_list
```

## 🎉 Success!

Your bot is now running! Check out:
- [USAGE.md](USAGE.md) for example workflows
- [README.md](README.md) for complete documentation

## Quick Reference

**Player Commands:**
- `/player_add` - Register a player
- `/player_addchar` - Add a character
- `/player_stats` - View stats
- `/player_list` - List all players

**Roster Commands:**
- `/roster_create` - Create a raid
- `/roster_add` - Add to roster
- `/roster_view` - View roster
- `/roster_list` - List raids

**Need Help?**

Common issues:
- **Bot offline?** Make sure `python bot.py` is running
- **Commands not showing?** Wait 5 minutes for Discord to sync, or restart the bot
- **Permission errors?** Check that the bot has proper roles in your server
- **Token error?** Verify your token in `.env` is correct (no extra spaces)

For detailed troubleshooting, see [README.md](README.md#troubleshooting).

## Next Steps

1. Read the [Usage Guide](USAGE.md) for example workflows
2. Register your guild members with `/player_add`
3. Add their characters with `/player_addchar`
4. Create your first raid with `/roster_create`
5. Build your roster with `/roster_add`

Happy raiding! 🎮
