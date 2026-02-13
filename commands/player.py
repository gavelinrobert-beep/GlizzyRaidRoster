"""Player management commands."""
import discord
from discord import app_commands
from discord.ext import commands
import logging
from database.db import Database
from utils.embeds import (
    create_error_embed, 
    create_success_embed,
    create_player_stats_embed,
    create_player_list_embed
)
from utils.validators import validate_player_name, validate_character_name, validate_class, validate_role

logger = logging.getLogger(__name__)


class PlayerCommands(commands.Cog):
    """Player management commands cog."""
    
    def __init__(self, bot: commands.Bot, db: Database):
        """Initialize player commands cog.
        
        Args:
            bot: Discord bot instance
            db: Database instance
        """
        self.bot = bot
        self.db = db
    
    @app_commands.command(name="player_add", description="Register a new player")
    @app_commands.describe(
        name="Player name",
        discord_user="Discord user to link to this player"
    )
    async def player_add(self, interaction: discord.Interaction, name: str, discord_user: discord.User):
        """Register a new player.
        
        Args:
            interaction: Discord interaction
            name: Player name
            discord_user: Discord user object
        """
        await interaction.response.defer()
        
        # Validate player name
        if not validate_player_name(name):
            await interaction.followup.send(embed=create_error_embed(
                "Invalid player name. Must be 2-50 characters."
            ))
            return
        
        # Add player to database
        player_id = await self.db.add_player(str(discord_user.id), name)
        
        if player_id:
            await interaction.followup.send(embed=create_success_embed(
                f"Player **{name}** registered successfully and linked to {discord_user.mention}."
            ))
            logger.info(f"Player {name} (ID: {player_id}) registered by {interaction.user}")
        else:
            await interaction.followup.send(embed=create_error_embed(
                f"Failed to register player. A player may already be linked to {discord_user.mention}."
            ))
    
    @app_commands.command(name="player_addchar", description="Add a character to a player")
    @app_commands.describe(
        player_name="Player name",
        character_name="Character name",
        wow_class="WoW class",
        role="Character role (Tank/Healer/DPS)"
    )
    async def player_addchar(self, interaction: discord.Interaction, 
                            player_name: str, character_name: str, 
                            wow_class: str, role: str = None):
        """Add a character to a player.
        
        Args:
            interaction: Discord interaction
            player_name: Player name
            character_name: Character name
            wow_class: WoW class
            role: Character role (optional)
        """
        await interaction.response.defer()
        
        # Validate character name
        if not validate_character_name(character_name):
            await interaction.followup.send(embed=create_error_embed(
                "Invalid character name. Must be 2-20 characters."
            ))
            return
        
        # Validate class
        validated_class = validate_class(wow_class)
        if not validated_class:
            await interaction.followup.send(embed=create_error_embed(
                f"Invalid class. Valid classes: Death Knight, Demon Hunter, Druid, Hunter, Mage, Monk, Paladin, Priest, Rogue, Shaman, Warlock, Warrior"
            ))
            return
        
        # Validate role if provided
        validated_role = None
        if role:
            validated_role = validate_role(role)
            if not validated_role:
                await interaction.followup.send(embed=create_error_embed(
                    "Invalid role. Valid roles: Tank, Healer, DPS"
                ))
                return
        
        # Get player
        player = await self.db.get_player_by_name(player_name)
        if not player:
            await interaction.followup.send(embed=create_error_embed(
                f"Player **{player_name}** not found. Use `/player_add` to register them first."
            ))
            return
        
        # Add character
        char_id = await self.db.add_character(
            player.player_id, 
            character_name, 
            validated_class, 
            validated_role
        )
        
        if char_id:
            role_text = f" ({validated_role})" if validated_role else ""
            await interaction.followup.send(embed=create_success_embed(
                f"Character **{character_name}** ({validated_class}{role_text}) added to **{player_name}**."
            ))
            logger.info(f"Character {character_name} added to player {player_name} by {interaction.user}")
        else:
            await interaction.followup.send(embed=create_error_embed(
                f"Failed to add character. **{character_name}** may already exist for this player."
            ))
    
    @app_commands.command(name="player_stats", description="Show player statistics")
    @app_commands.describe(player_name="Player name")
    async def player_stats(self, interaction: discord.Interaction, player_name: str):
        """Show player statistics.
        
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
    
    @app_commands.command(name="player_list", description="List all registered players")
    async def player_list(self, interaction: discord.Interaction):
        """List all registered players.
        
        Args:
            interaction: Discord interaction
        """
        await interaction.response.defer()
        
        # Get all players
        players = await self.db.get_all_players()
        
        # Create and send embed
        embed = create_player_list_embed(players)
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot, db: Database):
    """Setup function to add cog to bot.
    
    Args:
        bot: Discord bot instance
        db: Database instance
    """
    await bot.add_cog(PlayerCommands(bot, db))
