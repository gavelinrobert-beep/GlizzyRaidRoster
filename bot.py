"""Main Discord bot file for WoW Raid Roster management."""
import discord
from discord.ext import commands
import logging
import sys
from pathlib import Path

# Import configuration and database
from config import Config
from database.db import Database

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class RaidRosterBot(commands.Bot):
    """Main bot class for the WoW Raid Roster Discord bot."""
    
    def __init__(self, db: Database):
        """Initialize the bot.
        
        Args:
            db: Database instance
        """
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.members = True
        
        super().__init__(
            command_prefix="!",  # Fallback prefix, mainly using slash commands
            intents=intents,
            help_command=None
        )
        
        self.db = db
    
    async def setup_hook(self):
        """Setup hook called when bot is starting."""
        # Initialize database
        await self.db.initialize()
        logger.info("Database initialized")
        
        # Load command cogs
        try:
            from commands import player, roster, stats, swap
            await player.setup(self, self.db)
            await roster.setup(self, self.db)
            await stats.setup(self, self.db)
            await swap.setup(self, self.db)
            logger.info("All command cogs loaded")
        except Exception as e:
            logger.error(f"Failed to load command cogs: {e}")
            raise
        
        # Sync commands with Discord
        try:
            if Config.GUILD_ID:
                guild = discord.Object(id=Config.GUILD_ID)
                self.tree.copy_global_to(guild=guild)
                await self.tree.sync(guild=guild)
                logger.info(f"Commands synced to guild {Config.GUILD_ID}")
            else:
                await self.tree.sync()
                logger.info("Commands synced globally")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")
    
    async def on_ready(self):
        """Called when the bot is ready."""
        logger.info(f"Bot is ready! Logged in as {self.user} (ID: {self.user.id})")
        logger.info(f"Connected to {len(self.guilds)} guilds")
        
        # Set bot status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="raid rosters"
            )
        )
    
    async def on_command_error(self, ctx, error):
        """Handle command errors.
        
        Args:
            ctx: Command context
            error: Error that occurred
        """
        logger.error(f"Command error: {error}")
        
        if isinstance(error, commands.CommandNotFound):
            return
        
        await ctx.send(f"An error occurred: {str(error)}")
    
    async def on_app_command_error(self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
        """Handle application command errors.
        
        Args:
            interaction: Discord interaction
            error: Error that occurred
        """
        logger.error(f"App command error: {error}")
        
        error_message = f"An error occurred: {str(error)}"
        
        try:
            if interaction.response.is_done():
                await interaction.followup.send(error_message, ephemeral=True)
            else:
                await interaction.response.send_message(error_message, ephemeral=True)
        except Exception as e:
            logger.error(f"Failed to send error message: {e}")


async def main():
    """Main entry point for the bot."""
    # Validate configuration
    if not Config.validate():
        logger.error("Configuration validation failed. Check your .env file.")
        sys.exit(1)
    
    # Set logging level from config
    log_level = getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO)
    logging.getLogger().setLevel(log_level)
    
    # Initialize database
    db = Database(Config.DATABASE_PATH)
    
    # Create and run bot
    bot = RaidRosterBot(db)
    
    try:
        logger.info("Starting bot...")
        await bot.start(Config.DISCORD_TOKEN)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot encountered an error: {e}")
        raise
    finally:
        await bot.close()
        logger.info("Bot shut down")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
