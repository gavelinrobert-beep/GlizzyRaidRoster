# GlizzyRaidRoster

A Discord bot for managing World of Warcraft guild raid rosters. Replace your Google Sheets workflow with an integrated Discord solution featuring slash commands, player tracking, and beautiful color-coded roster displays.

## Features

- **Slash Commands**: Modern Discord interactions for all bot operations
- **Player Management**: Register players, add characters with WoW classes and roles
- **Roster Management**: Create raids, assign players, manage benches and absences
- **Statistics Tracking**: Track raids rostered, benches, and guild-wide statistics
- **Color-Coded Displays**: Beautiful embeds matching WoW class colors
- **Flexible Date Input**: Support for various date formats (YYYY-MM-DD, DD/MM/YYYY, "19th Feb", etc.)
- **Permission System**: Role-based access control for roster modifications
- **SQLite Database**: Persistent data storage with automatic backups

## Prerequisites

- **Python 3.8+** (Python 3.10+ recommended)
- **Discord Bot Account** with proper permissions
- **Server Administrator Access** to install the bot

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/gavelinrobert-beep/GlizzyRaidRoster.git
cd GlizzyRaidRoster
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Or use a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Create Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to the "Bot" section
4. Click "Add Bot"
5. Under "Privileged Gateway Intents", enable:
   - Server Members Intent
   - Message Content Intent
6. Click "Reset Token" and copy your bot token (keep this secret!)
7. Go to "OAuth2" > "URL Generator"
8. Select scopes: `bot` and `applications.commands`
9. Select bot permissions:
   - Read Messages/View Channels
   - Send Messages
   - Embed Links
   - Read Message History
   - Use Slash Commands
10. Copy the generated URL and open it in your browser to invite the bot to your server

### 4. Configure the Bot

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your configuration:
   ```env
   DISCORD_TOKEN=your_discord_bot_token_here
   GUILD_ID=your_guild_id_here
   DATABASE_PATH=database/raid_roster.db
   AUTHORIZED_ROLES=Officer,Raid Leader
   LOG_LEVEL=INFO
   ```

   **Getting your Guild ID:**
   - Enable Developer Mode in Discord (User Settings > Advanced > Developer Mode)
   - Right-click your server icon and click "Copy ID"

### 5. Run the Bot

```bash
python bot.py
```

The bot will:
1. Create the database and tables automatically
2. Load all commands
3. Sync slash commands with your Discord server
4. Start listening for commands

## Command Reference

For a complete list of commands and usage examples, see the [Commands Documentation](docs/COMMANDS.md).

### Quick Command Overview

**Player Management:**
- `/player_add` - Register a new player
- `/player_addchar` - Add a character to a player
- `/player_stats` - View player statistics
- `/player_list` - List all players

**Roster Management:**
- `/roster_create` - Create a new raid
- `/roster_add` - Add player to raid
- `/roster_remove` - Remove player from raid
- `/roster_bench` - Move player to bench
- `/roster_absence` - Mark player as absent
- `/roster_swap` - Record a swap between players
- `/roster_view` - Display raid roster
- `/roster_list` - List all raids

**Statistics:**
- `/stats_player` - Player statistics
- `/stats_overview` - Guild overview

## Database Schema

The bot uses SQLite with four main tables:
- **players**: Player information and statistics
- **characters**: Character data linked to players
- **raids**: Raid event information
- **roster_assignments**: Player assignments to raids

For detailed schema information, see [Database Documentation](docs/DATABASE.md).

## Troubleshooting

### Bot doesn't respond to commands
1. Check that the bot is online (green status in Discord)
2. Verify the bot has proper permissions in your server
3. Try kicking and re-inviting the bot with the correct permissions
4. Check `bot.log` for errors

### Commands don't appear in Discord
1. Make sure you've set the correct `GUILD_ID` in `.env`
2. Wait a few minutes for commands to sync
3. Try restarting the bot
4. Check that you invited the bot with `applications.commands` scope

### "Configuration validation failed" error
- Ensure `.env` file exists and has valid values
- Check that `DISCORD_TOKEN` is set correctly
- Verify `GUILD_ID` is a valid number

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is provided as-is for guild use. Feel free to modify and adapt for your needs.

## Credits

Built with:
- [discord.py](https://github.com/Rapptz/discord.py) - Discord API wrapper
- [aiosqlite](https://github.com/omnilib/aiosqlite) - Async SQLite
- [python-dateutil](https://github.com/dateutil/dateutil) - Date parsing
- [python-dotenv](https://github.com/theskumar/python-dotenv) - Environment management
