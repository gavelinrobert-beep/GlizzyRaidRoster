"""Roster management commands."""
import discord
from discord import app_commands
from discord.ext import commands
import logging
from database.db import Database
from utils.embeds import (
    create_error_embed, 
    create_success_embed,
    create_roster_embed,
    create_raid_list_embed
)
from utils.validators import validate_date

logger = logging.getLogger(__name__)


class RosterCommands(commands.Cog):
    """Roster management commands cog."""
    
    def __init__(self, bot: commands.Bot, db: Database):
        """Initialize roster commands cog.
        
        Args:
            bot: Discord bot instance
            db: Database instance
        """
        self.bot = bot
        self.db = db
    
    @app_commands.command(name="roster_create", description="Create a new raid event")
    @app_commands.describe(
        date="Raid date (YYYY-MM-DD or flexible format)",
        time="Raid time (optional)",
        timezone="Timezone (default: Server Time)"
    )
    async def roster_create(self, interaction: discord.Interaction, 
                           date: str, time: str = None, timezone: str = "Server Time"):
        """Create a new raid event.
        
        Args:
            interaction: Discord interaction
            date: Raid date
            time: Raid time (optional)
            timezone: Timezone
        """
        await interaction.response.defer()
        
        # Validate date
        validated_date = validate_date(date)
        if not validated_date:
            await interaction.followup.send(embed=create_error_embed(
                f"Invalid date format: **{date}**. Try formats like: 2024-02-19, 19/02/2024, or '19th Feb'"
            ))
            return
        
        # Create raid
        raid_id = await self.db.create_raid(validated_date, time, timezone)
        
        if raid_id:
            time_text = f" at {time}" if time else ""
            await interaction.followup.send(embed=create_success_embed(
                f"Raid created for **{validated_date}**{time_text} {timezone}."
            ))
            logger.info(f"Raid created for {validated_date} by {interaction.user}")
        else:
            await interaction.followup.send(embed=create_error_embed(
                f"Failed to create raid. A raid for **{validated_date}** already exists."
            ))
    
    @app_commands.command(name="roster_add", description="Add player to main roster")
    @app_commands.describe(
        raid_date="Raid date",
        player_name="Player name",
        character_name="Character name",
        position="Position number (optional)"
    )
    async def roster_add(self, interaction: discord.Interaction, 
                        raid_date: str, player_name: str, 
                        character_name: str, position: int = None):
        """Add player to main roster.
        
        Args:
            interaction: Discord interaction
            raid_date: Raid date
            player_name: Player name
            character_name: Character name
            position: Position in roster (optional)
        """
        await interaction.response.defer()
        
        # Validate date
        validated_date = validate_date(raid_date)
        if not validated_date:
            await interaction.followup.send(embed=create_error_embed(
                f"Invalid date format: **{raid_date}**"
            ))
            return
        
        # Get raid
        raid = await self.db.get_raid_by_date(validated_date)
        if not raid:
            await interaction.followup.send(embed=create_error_embed(
                f"No raid found for **{validated_date}**. Create one first with `/roster_create`."
            ))
            return
        
        # Get player
        player = await self.db.get_player_by_name(player_name)
        if not player:
            await interaction.followup.send(embed=create_error_embed(
                f"Player **{player_name}** not found. Use `/player_add` to register them first."
            ))
            return
        
        # Add roster assignment
        assignment_id = await self.db.add_roster_assignment(
            raid.raid_id, 
            player.player_id, 
            character_name, 
            position, 
            "main"
        )
        
        if assignment_id:
            await interaction.followup.send(embed=create_success_embed(
                f"**{player_name}** ({character_name}) added to main roster for **{validated_date}**."
            ))
            logger.info(f"{player_name} added to raid {validated_date} by {interaction.user}")
        else:
            await interaction.followup.send(embed=create_error_embed(
                f"Failed to add player. **{player_name}** may already be assigned to this raid."
            ))
    
    @app_commands.command(name="roster_remove", description="Remove player from roster")
    @app_commands.describe(
        raid_date="Raid date",
        player_name="Player name"
    )
    async def roster_remove(self, interaction: discord.Interaction, 
                           raid_date: str, player_name: str):
        """Remove player from roster.
        
        Args:
            interaction: Discord interaction
            raid_date: Raid date
            player_name: Player name
        """
        await interaction.response.defer()
        
        # Validate date
        validated_date = validate_date(raid_date)
        if not validated_date:
            await interaction.followup.send(embed=create_error_embed(
                f"Invalid date format: **{raid_date}**"
            ))
            return
        
        # Get raid
        raid = await self.db.get_raid_by_date(validated_date)
        if not raid:
            await interaction.followup.send(embed=create_error_embed(
                f"No raid found for **{validated_date}**."
            ))
            return
        
        # Get player
        player = await self.db.get_player_by_name(player_name)
        if not player:
            await interaction.followup.send(embed=create_error_embed(
                f"Player **{player_name}** not found."
            ))
            return
        
        # Remove roster assignment
        await self.db.remove_roster_assignment(raid.raid_id, player.player_id)
        
        await interaction.followup.send(embed=create_success_embed(
            f"**{player_name}** removed from roster for **{validated_date}**."
        ))
        logger.info(f"{player_name} removed from raid {validated_date} by {interaction.user}")
    
    @app_commands.command(name="roster_bench", description="Move player to bench")
    @app_commands.describe(
        raid_date="Raid date",
        player_name="Player name"
    )
    async def roster_bench(self, interaction: discord.Interaction, 
                          raid_date: str, player_name: str):
        """Move player to bench.
        
        Args:
            interaction: Discord interaction
            raid_date: Raid date
            player_name: Player name
        """
        await interaction.response.defer()
        
        # Validate date
        validated_date = validate_date(raid_date)
        if not validated_date:
            await interaction.followup.send(embed=create_error_embed(
                f"Invalid date format: **{raid_date}**"
            ))
            return
        
        # Get raid
        raid = await self.db.get_raid_by_date(validated_date)
        if not raid:
            await interaction.followup.send(embed=create_error_embed(
                f"No raid found for **{validated_date}**."
            ))
            return
        
        # Get player
        player = await self.db.get_player_by_name(player_name)
        if not player:
            await interaction.followup.send(embed=create_error_embed(
                f"Player **{player_name}** not found."
            ))
            return
        
        # Update status to bench
        await self.db.update_roster_assignment_status(raid.raid_id, player.player_id, "bench")
        
        await interaction.followup.send(embed=create_success_embed(
            f"**{player_name}** moved to bench for **{validated_date}**."
        ))
        logger.info(f"{player_name} benched for raid {validated_date} by {interaction.user}")
    
    @app_commands.command(name="roster_absence", description="Mark player as absent")
    @app_commands.describe(
        raid_date="Raid date",
        player_name="Player name"
    )
    async def roster_absence(self, interaction: discord.Interaction, 
                            raid_date: str, player_name: str):
        """Mark player as absent.
        
        Args:
            interaction: Discord interaction
            raid_date: Raid date
            player_name: Player name
        """
        await interaction.response.defer()
        
        # Validate date
        validated_date = validate_date(raid_date)
        if not validated_date:
            await interaction.followup.send(embed=create_error_embed(
                f"Invalid date format: **{raid_date}**"
            ))
            return
        
        # Get raid
        raid = await self.db.get_raid_by_date(validated_date)
        if not raid:
            await interaction.followup.send(embed=create_error_embed(
                f"No raid found for **{validated_date}**."
            ))
            return
        
        # Get player
        player = await self.db.get_player_by_name(player_name)
        if not player:
            await interaction.followup.send(embed=create_error_embed(
                f"Player **{player_name}** not found."
            ))
            return
        
        # Update status to absent
        await self.db.update_roster_assignment_status(raid.raid_id, player.player_id, "absent")
        
        await interaction.followup.send(embed=create_success_embed(
            f"**{player_name}** marked as absent for **{validated_date}**."
        ))
        logger.info(f"{player_name} marked absent for raid {validated_date} by {interaction.user}")
    
    @app_commands.command(name="roster_swap", description="Swap two players")
    @app_commands.describe(
        raid_date="Raid date",
        player1="First player name",
        player2="Second player name"
    )
    async def roster_swap(self, interaction: discord.Interaction, 
                         raid_date: str, player1: str, player2: str):
        """Swap two players.
        
        Args:
            interaction: Discord interaction
            raid_date: Raid date
            player1: First player name
            player2: Second player name
        """
        await interaction.response.defer()
        
        # Validate date
        validated_date = validate_date(raid_date)
        if not validated_date:
            await interaction.followup.send(embed=create_error_embed(
                f"Invalid date format: **{raid_date}**"
            ))
            return
        
        # Get raid
        raid = await self.db.get_raid_by_date(validated_date)
        if not raid:
            await interaction.followup.send(embed=create_error_embed(
                f"No raid found for **{validated_date}**."
            ))
            return
        
        # Get both players
        p1 = await self.db.get_player_by_name(player1)
        p2 = await self.db.get_player_by_name(player2)
        
        if not p1:
            await interaction.followup.send(embed=create_error_embed(
                f"Player **{player1}** not found."
            ))
            return
        
        if not p2:
            await interaction.followup.send(embed=create_error_embed(
                f"Player **{player2}** not found."
            ))
            return
        
        # Mark both as swap status
        await self.db.update_roster_assignment_status(raid.raid_id, p1.player_id, "swap")
        await self.db.update_roster_assignment_status(raid.raid_id, p2.player_id, "swap")
        
        await interaction.followup.send(embed=create_success_embed(
            f"Swap recorded between **{player1}** and **{player2}** for **{validated_date}**."
        ))
        logger.info(f"Swap recorded for {player1} and {player2} on {validated_date} by {interaction.user}")
    
    @app_commands.command(name="roster_view", description="Display the raid roster")
    @app_commands.describe(raid_date="Raid date")
    async def roster_view(self, interaction: discord.Interaction, raid_date: str):
        """Display the raid roster.
        
        Args:
            interaction: Discord interaction
            raid_date: Raid date
        """
        await interaction.response.defer()
        
        # Validate date
        validated_date = validate_date(raid_date)
        if not validated_date:
            await interaction.followup.send(embed=create_error_embed(
                f"Invalid date format: **{raid_date}**"
            ))
            return
        
        # Get raid
        raid = await self.db.get_raid_by_date(validated_date)
        if not raid:
            await interaction.followup.send(embed=create_error_embed(
                f"No raid found for **{validated_date}**. Create one first with `/roster_create`."
            ))
            return
        
        # Get roster
        roster_data = await self.db.get_raid_roster(raid.raid_id)
        
        # Create and send embed
        embed = create_roster_embed(raid, roster_data)
        
        # Add pending swaps section
        pending_swaps = await self.db.get_pending_swap_requests(raid.raid_id)
        if pending_swaps:
            all_players = await self.db.get_all_players()
            swap_text = []
            for swap in pending_swaps:
                requesting_player = next((p for p in all_players if p.player_id == swap.requesting_player_id), None)
                if requesting_player:
                    swap_info = f"• Request #{swap.request_id}: {requesting_player.player_name}"
                    if swap.accepting_player_id:
                        accepting_player = next((p for p in all_players if p.player_id == swap.accepting_player_id), None)
                        if accepting_player:
                            swap_info += f" ↔ {accepting_player.player_name}"
                    swap_text.append(swap_info)
            
            if swap_text:
                embed.add_field(
                    name=f"🔄 Pending Swaps ({len(pending_swaps)})",
                    value="\n".join(swap_text),
                    inline=False
                )
        
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="roster_list", description="List all upcoming raids")
    async def roster_list(self, interaction: discord.Interaction):
        """List all upcoming raids.
        
        Args:
            interaction: Discord interaction
        """
        await interaction.response.defer()
        
        # Get all raids
        raids = await self.db.get_all_raids()
        
        # Create and send embed
        embed = create_raid_list_embed(raids)
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="roster_calendar", description="Generate visual roster calendar")
    @app_commands.describe(weeks="Number of weeks to display (default: 4)")
    async def roster_calendar(self, interaction: discord.Interaction, weeks: int = 4):
        """Generate and display a visual roster calendar.
        
        Args:
            interaction: Discord interaction
            weeks: Number of weeks to display
        """
        await interaction.response.defer()
        
        # Validate weeks parameter
        if weeks < 1 or weeks > 12:
            await interaction.followup.send(embed=create_error_embed(
                "Weeks parameter must be between 1 and 12."
            ))
            return
        
        try:
            # Get upcoming raids with roster data
            raids_data = await self.db.get_upcoming_raids_with_roster(weeks)
            
            if not raids_data:
                await interaction.followup.send(embed=create_error_embed(
                    "No upcoming raids found. Create raids with `/roster_create` first."
                ))
                return
            
            # Get all players for stats column
            all_players = await self.db.get_all_players()
            
            if not all_players:
                await interaction.followup.send(embed=create_error_embed(
                    "No players registered. Add players with `/player_add` first."
                ))
                return
            
            # Generate image
            from utils.image_generator import generate_roster_calendar
            image_buffer = generate_roster_calendar(raids_data, all_players)
            
            # Create Discord file
            file = discord.File(image_buffer, filename="roster_calendar.png")
            
            # Create embed with image
            embed = discord.Embed(
                title=f"📅 Roster Calendar - Next {weeks} Weeks",
                color=0x5865F2
            )
            embed.set_image(url="attachment://roster_calendar.png")
            embed.set_footer(text=f"Showing {len(raids_data)} raids with {len(all_players)} players")
            
            await interaction.followup.send(embed=embed, file=file)
            logger.info(f"Roster calendar generated for {weeks} weeks by {interaction.user}")
            
        except Exception as e:
            logger.error(f"Failed to generate roster calendar: {e}")
            await interaction.followup.send(embed=create_error_embed(
                f"Failed to generate calendar: {str(e)}"
            ))


async def setup(bot: commands.Bot, db: Database):
    """Setup function to add cog to bot.
    
    Args:
        bot: Discord bot instance
        db: Database instance
    """
    await bot.add_cog(RosterCommands(bot, db))
