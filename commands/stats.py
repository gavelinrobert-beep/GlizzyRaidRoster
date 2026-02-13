"""Statistics commands."""
import discord
from discord import app_commands
from discord.ext import commands
import logging
from database.db import Database
from utils.embeds import (
    create_error_embed,
    create_player_stats_embed,
    create_overview_stats_embed
)

logger = logging.getLogger(__name__)


class StatsCommands(commands.Cog):
    """Statistics commands cog."""
    
    def __init__(self, bot: commands.Bot, db: Database):
        """Initialize stats commands cog.
        
        Args:
            bot: Discord bot instance
            db: Database instance
        """
        self.bot = bot
        self.db = db
    
    @app_commands.command(name="stats_player", description="Show detailed player statistics")
    @app_commands.describe(player_name="Player name")
    async def stats_player(self, interaction: discord.Interaction, player_name: str):
        """Show detailed player statistics.
        
        Args:
            interaction: Discord interaction
            player_name: Player name
        """
        await interaction.response.defer()
        
        # Get player
        player = await self.db.get_player_by_name(player_name)
        if not player:
            await interaction.followup.send(embed=create_error_embed(
                f"Player **{player_name}** not found."
            ))
            return
        
        # Get player characters
        characters = await self.db.get_player_characters(player.player_id)
        
        # Create and send embed
        embed = create_player_stats_embed(player, characters)
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="stats_overview", description="Show guild-wide statistics")
    async def stats_overview(self, interaction: discord.Interaction):
        """Show guild-wide statistics.
        
        Args:
            interaction: Discord interaction
        """
        await interaction.response.defer()
        
        # Get counts
        players = await self.db.get_all_players()
        raids = await self.db.get_all_raids()
        
        # Count total assignments efficiently
        total_assignments = await self.db.count_total_assignments()
        
        # Create and send embed
        embed = create_overview_stats_embed(len(players), len(raids), total_assignments)
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot, db: Database):
    """Setup function to add cog to bot.
    
    Args:
        bot: Discord bot instance
        db: Database instance
    """
    await bot.add_cog(StatsCommands(bot, db))
