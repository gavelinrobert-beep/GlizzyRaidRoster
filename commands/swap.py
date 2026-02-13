"""Swap request management commands."""
import discord
from discord import app_commands
from discord.ext import commands
import logging
from typing import Optional
from database.db import Database
from utils.embeds import create_error_embed, create_success_embed
from utils.validators import validate_date
from config import Config

logger = logging.getLogger(__name__)


def create_swap_request_embed(swap_request, raid, requesting_player, accepting_player=None) -> discord.Embed:
    """Create an embed for a swap request.
    
    Args:
        swap_request: SwapRequest object
        raid: Raid object
        requesting_player: Player object
        accepting_player: Optional Player object
        
    Returns:
        Discord embed
    """
    if swap_request.status == "pending":
        title = "🔄 New Swap Request"
        color = 0xFFA500  # Orange
    elif swap_request.status == "accepted":
        title = "✅ Swap Request Accepted"
        color = 0x00FF00  # Green
    elif swap_request.status == "approved":
        title = "✅ Swap Request Approved"
        color = 0x00FF00  # Green
    elif swap_request.status == "denied":
        title = "❌ Swap Request Denied"
        color = 0xFF0000  # Red
    else:
        title = "🔄 Swap Request"
        color = 0x5865F2  # Default blue
    
    embed = discord.Embed(
        title=title,
        color=color
    )
    
    embed.add_field(name="Request ID", value=f"#{swap_request.request_id}", inline=True)
    embed.add_field(name="Raid Date", value=raid.raid_date, inline=True)
    embed.add_field(name="Status", value=swap_request.status.upper(), inline=True)
    
    embed.add_field(name="Requesting Player", value=requesting_player.player_name, inline=True)
    
    if accepting_player:
        embed.add_field(name="Accepting Player", value=accepting_player.player_name, inline=True)
    
    if swap_request.reason:
        embed.add_field(name="Reason", value=swap_request.reason, inline=False)
    
    if swap_request.status == "pending":
        embed.set_footer(text="Bench players can accept with /swap_accept <request_id>")
    
    return embed


class SwapCommands(commands.Cog):
    """Swap request management commands cog."""
    
    def __init__(self, bot: commands.Bot, db: Database):
        """Initialize swap commands cog.
        
        Args:
            bot: Discord bot instance
            db: Database instance
        """
        self.bot = bot
        self.db = db
    
    @app_commands.command(name="swap_request", description="Request to swap out of main roster")
    @app_commands.describe(
        raid_date="Raid date",
        reason="Optional reason for the swap request"
    )
    async def swap_request(self, interaction: discord.Interaction, 
                          raid_date: str, reason: Optional[str] = None):
        """Create a swap request.
        
        Args:
            interaction: Discord interaction
            raid_date: Raid date
            reason: Optional reason for swap
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
        player = await self.db.get_player_by_discord_id(str(interaction.user.id))
        if not player:
            await interaction.followup.send(embed=create_error_embed(
                "You are not registered. Ask an officer to add you with `/player_add`."
            ))
            return
        
        # Check if player is on main roster for this raid
        roster_data = await self.db.get_raid_roster(raid.raid_id)
        player_assignment = None
        for assignment, p, class_name in roster_data:
            if p.player_id == player.player_id:
                player_assignment = assignment
                break
        
        if not player_assignment:
            await interaction.followup.send(embed=create_error_embed(
                f"You are not assigned to the raid on **{validated_date}**."
            ))
            return
        
        if player_assignment.status != "main":
            await interaction.followup.send(embed=create_error_embed(
                f"Only main roster players can request swaps. Your status is: **{player_assignment.status}**"
            ))
            return
        
        # Check for existing pending request
        pending_requests = await self.db.get_pending_swap_requests(raid.raid_id)
        for req in pending_requests:
            if req.requesting_player_id == player.player_id:
                await interaction.followup.send(embed=create_error_embed(
                    f"You already have a pending swap request for this raid (Request #{req.request_id})."
                ))
                return
        
        # Create swap request
        request_id = await self.db.create_swap_request(raid.raid_id, player.player_id, reason)
        
        if request_id:
            swap_request = await self.db.get_swap_request(request_id)
            embed = create_swap_request_embed(swap_request, raid, player)
            
            await interaction.followup.send(embed=create_success_embed(
                f"Swap request created for **{validated_date}** (Request #{request_id}).\n"
                "Bench players can now accept this request."
            ))
            
            # Send notification to swap channel if configured
            if Config.SWAP_CHANNEL_ID:
                try:
                    channel = self.bot.get_channel(Config.SWAP_CHANNEL_ID)
                    if channel:
                        await channel.send(embed=embed)
                except Exception as e:
                    logger.error(f"Failed to send swap notification: {e}")
            
            logger.info(f"Swap request #{request_id} created by {player.player_name} for {validated_date}")
        else:
            await interaction.followup.send(embed=create_error_embed(
                "Failed to create swap request. Please try again."
            ))
    
    @app_commands.command(name="swap_accept", description="Accept a swap request")
    @app_commands.describe(request_id="Swap request ID")
    async def swap_accept(self, interaction: discord.Interaction, request_id: int):
        """Accept a swap request.
        
        Args:
            interaction: Discord interaction
            request_id: Swap request ID
        """
        await interaction.response.defer()
        
        # Get swap request
        swap_request = await self.db.get_swap_request(request_id)
        if not swap_request:
            await interaction.followup.send(embed=create_error_embed(
                f"Swap request #{request_id} not found."
            ))
            return
        
        if swap_request.status != "pending":
            await interaction.followup.send(embed=create_error_embed(
                f"This swap request is no longer pending (status: {swap_request.status})."
            ))
            return
        
        # Get accepting player
        accepting_player = await self.db.get_player_by_discord_id(str(interaction.user.id))
        if not accepting_player:
            await interaction.followup.send(embed=create_error_embed(
                "You are not registered. Ask an officer to add you with `/player_add`."
            ))
            return
        
        # Get requesting player
        all_players = await self.db.get_all_players()
        requesting_player = next((p for p in all_players if p.player_id == swap_request.requesting_player_id), None)
        
        if not requesting_player:
            await interaction.followup.send(embed=create_error_embed(
                "Could not find requesting player."
            ))
            return
        
        # Check if accepting player is different from requesting player
        if accepting_player.player_id == requesting_player.player_id:
            await interaction.followup.send(embed=create_error_embed(
                "You cannot accept your own swap request."
            ))
            return
        
        # Get raid
        all_raids = await self.db.get_all_raids()
        raid = next((r for r in all_raids if r.raid_id == swap_request.raid_id), None)
        
        if not raid:
            await interaction.followup.send(embed=create_error_embed(
                "Could not find the raid for this swap request."
            ))
            return
        
        # Check if accepting player is on bench for this raid
        roster_data = await self.db.get_raid_roster(raid.raid_id)
        accepting_assignment = None
        requesting_assignment = None
        
        for assignment, p, class_name in roster_data:
            if p.player_id == accepting_player.player_id:
                accepting_assignment = assignment
            if p.player_id == requesting_player.player_id:
                requesting_assignment = assignment
        
        if not accepting_assignment:
            await interaction.followup.send(embed=create_error_embed(
                f"You are not assigned to the raid on **{raid.raid_date}**."
            ))
            return
        
        if accepting_assignment.status != "bench":
            await interaction.followup.send(embed=create_error_embed(
                f"Only bench players can accept swaps. Your status is: **{accepting_assignment.status}**"
            ))
            return
        
        if not requesting_assignment or requesting_assignment.status != "main":
            await interaction.followup.send(embed=create_error_embed(
                "The requesting player is no longer on the main roster."
            ))
            return
        
        # Execute the swap
        try:
            # Update swap request status
            if Config.AUTO_APPROVE_SWAPS:
                # Auto-approve and execute immediately
                await self.db.update_swap_request_status(request_id, "approved", accepting_player.player_id)
                
                # Swap the assignments
                await self.db.update_roster_assignment_status(raid.raid_id, requesting_player.player_id, "bench")
                await self.db.update_roster_assignment_status(raid.raid_id, accepting_player.player_id, "main")
                
                # Update player stats
                await self.db.update_player_stats(requesting_player.player_id, raids_rostered=-1, benches=1)
                await self.db.update_player_stats(accepting_player.player_id, raids_rostered=1, benches=-1)
                
                await interaction.followup.send(embed=create_success_embed(
                    f"Swap executed! **{requesting_player.player_name}** → Bench, **{accepting_player.player_name}** → Main Roster"
                ))
                
                logger.info(f"Swap #{request_id} auto-approved and executed between {requesting_player.player_name} and {accepting_player.player_name}")
            else:
                # Mark as accepted, waiting for officer approval
                await self.db.update_swap_request_status(request_id, "accepted", accepting_player.player_id)
                
                await interaction.followup.send(embed=create_success_embed(
                    f"You have accepted the swap request. Waiting for officer approval.\n"
                    f"Request ID: #{request_id}"
                ))
                
                # Notify officers
                if Config.SWAP_CHANNEL_ID:
                    try:
                        channel = self.bot.get_channel(Config.SWAP_CHANNEL_ID)
                        if channel:
                            swap_request = await self.db.get_swap_request(request_id)
                            embed = create_swap_request_embed(swap_request, raid, requesting_player, accepting_player)
                            
                            # Mention officers if role is configured
                            mention_text = ""
                            if Config.AUTHORIZED_ROLES:
                                guild = interaction.guild
                                if guild:
                                    for role_name in Config.AUTHORIZED_ROLES:
                                        role = discord.utils.get(guild.roles, name=role_name)
                                        if role:
                                            mention_text = f"{role.mention} "
                                            break
                            
                            await channel.send(content=f"{mention_text}Approval needed!", embed=embed)
                    except Exception as e:
                        logger.error(f"Failed to send swap notification: {e}")
                
                logger.info(f"Swap #{request_id} accepted by {accepting_player.player_name}, awaiting approval")
        except Exception as e:
            logger.error(f"Failed to execute swap: {e}")
            await interaction.followup.send(embed=create_error_embed(
                f"Failed to process swap: {str(e)}"
            ))
    
    @app_commands.command(name="swap_list", description="List all pending swap requests")
    async def swap_list(self, interaction: discord.Interaction):
        """List all pending swap requests.
        
        Args:
            interaction: Discord interaction
        """
        await interaction.response.defer()
        
        # Get all pending requests
        pending_requests = await self.db.get_pending_swap_requests()
        
        if not pending_requests:
            await interaction.followup.send(embed=create_success_embed(
                "No pending swap requests."
            ))
            return
        
        # Create embed
        embed = discord.Embed(
            title="📋 Pending Swap Requests",
            color=0x5865F2
        )
        
        all_players = await self.db.get_all_players()
        all_raids = await self.db.get_all_raids()
        
        for swap_request in pending_requests:
            requesting_player = next((p for p in all_players if p.player_id == swap_request.requesting_player_id), None)
            raid = next((r for r in all_raids if r.raid_id == swap_request.raid_id), None)
            
            if requesting_player and raid:
                value = f"**Player:** {requesting_player.player_name}\n"
                value += f"**Raid:** {raid.raid_date}\n"
                if swap_request.reason:
                    value += f"**Reason:** {swap_request.reason}\n"
                if swap_request.accepting_player_id:
                    accepting_player = next((p for p in all_players if p.player_id == swap_request.accepting_player_id), None)
                    if accepting_player:
                        value += f"**Accepted by:** {accepting_player.player_name}\n"
                
                embed.add_field(
                    name=f"Request #{swap_request.request_id}",
                    value=value,
                    inline=False
                )
        
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="swap_approve", description="Approve a swap request (Officers only)")
    @app_commands.describe(request_id="Swap request ID")
    async def swap_approve(self, interaction: discord.Interaction, request_id: int):
        """Approve a swap request.
        
        Args:
            interaction: Discord interaction
            request_id: Swap request ID
        """
        await interaction.response.defer()
        
        # Check if user has permission (officer role)
        has_permission = False
        for role in interaction.user.roles:
            if role.name in Config.AUTHORIZED_ROLES:
                has_permission = True
                break
        
        if not has_permission:
            await interaction.followup.send(embed=create_error_embed(
                "You don't have permission to approve swap requests. Officer role required."
            ))
            return
        
        # Get swap request
        swap_request = await self.db.get_swap_request(request_id)
        if not swap_request:
            await interaction.followup.send(embed=create_error_embed(
                f"Swap request #{request_id} not found."
            ))
            return
        
        if swap_request.status not in ["pending", "accepted"]:
            await interaction.followup.send(embed=create_error_embed(
                f"Cannot approve request in status: {swap_request.status}"
            ))
            return
        
        if not swap_request.accepting_player_id:
            await interaction.followup.send(embed=create_error_embed(
                "No player has accepted this swap request yet."
            ))
            return
        
        # Get players and raid
        all_players = await self.db.get_all_players()
        all_raids = await self.db.get_all_raids()
        
        requesting_player = next((p for p in all_players if p.player_id == swap_request.requesting_player_id), None)
        accepting_player = next((p for p in all_players if p.player_id == swap_request.accepting_player_id), None)
        raid = next((r for r in all_raids if r.raid_id == swap_request.raid_id), None)
        
        if not (requesting_player and accepting_player and raid):
            await interaction.followup.send(embed=create_error_embed(
                "Could not find required data for this swap."
            ))
            return
        
        try:
            # Update swap request status
            await self.db.update_swap_request_status(request_id, "approved", swap_request.accepting_player_id)
            
            # Execute the swap
            await self.db.update_roster_assignment_status(raid.raid_id, requesting_player.player_id, "bench")
            await self.db.update_roster_assignment_status(raid.raid_id, accepting_player.player_id, "main")
            
            # Update player stats
            await self.db.update_player_stats(requesting_player.player_id, raids_rostered=-1, benches=1)
            await self.db.update_player_stats(accepting_player.player_id, raids_rostered=1, benches=-1)
            
            await interaction.followup.send(embed=create_success_embed(
                f"Swap approved and executed!\n"
                f"**{requesting_player.player_name}** → Bench\n"
                f"**{accepting_player.player_name}** → Main Roster"
            ))
            
            logger.info(f"Swap #{request_id} approved by {interaction.user} and executed")
        except Exception as e:
            logger.error(f"Failed to approve swap: {e}")
            await interaction.followup.send(embed=create_error_embed(
                f"Failed to approve swap: {str(e)}"
            ))
    
    @app_commands.command(name="swap_deny", description="Deny a swap request (Officers only)")
    @app_commands.describe(
        request_id="Swap request ID",
        reason="Optional reason for denial"
    )
    async def swap_deny(self, interaction: discord.Interaction, 
                       request_id: int, reason: Optional[str] = None):
        """Deny a swap request.
        
        Args:
            interaction: Discord interaction
            request_id: Swap request ID
            reason: Optional reason for denial
        """
        await interaction.response.defer()
        
        # Check if user has permission
        has_permission = False
        for role in interaction.user.roles:
            if role.name in Config.AUTHORIZED_ROLES:
                has_permission = True
                break
        
        if not has_permission:
            await interaction.followup.send(embed=create_error_embed(
                "You don't have permission to deny swap requests. Officer role required."
            ))
            return
        
        # Get swap request
        swap_request = await self.db.get_swap_request(request_id)
        if not swap_request:
            await interaction.followup.send(embed=create_error_embed(
                f"Swap request #{request_id} not found."
            ))
            return
        
        if swap_request.status not in ["pending", "accepted"]:
            await interaction.followup.send(embed=create_error_embed(
                f"Cannot deny request in status: {swap_request.status}"
            ))
            return
        
        # Update status to denied
        await self.db.update_swap_request_status(request_id, "denied")
        
        reason_text = f"\n**Reason:** {reason}" if reason else ""
        await interaction.followup.send(embed=create_success_embed(
            f"Swap request #{request_id} has been denied.{reason_text}"
        ))
        
        logger.info(f"Swap #{request_id} denied by {interaction.user}")
    
    @app_commands.command(name="swap_cancel", description="Cancel a swap request")
    @app_commands.describe(request_id="Swap request ID")
    async def swap_cancel(self, interaction: discord.Interaction, request_id: int):
        """Cancel a swap request.
        
        Args:
            interaction: Discord interaction
            request_id: Swap request ID
        """
        await interaction.response.defer()
        
        # Get swap request
        swap_request = await self.db.get_swap_request(request_id)
        if not swap_request:
            await interaction.followup.send(embed=create_error_embed(
                f"Swap request #{request_id} not found."
            ))
            return
        
        if swap_request.status not in ["pending", "accepted"]:
            await interaction.followup.send(embed=create_error_embed(
                f"Cannot cancel request in status: {swap_request.status}"
            ))
            return
        
        # Get player
        player = await self.db.get_player_by_discord_id(str(interaction.user.id))
        if not player:
            await interaction.followup.send(embed=create_error_embed(
                "You are not registered."
            ))
            return
        
        # Check if user is the requesting player or has officer permission
        is_requester = player.player_id == swap_request.requesting_player_id
        has_permission = False
        for role in interaction.user.roles:
            if role.name in Config.AUTHORIZED_ROLES:
                has_permission = True
                break
        
        if not (is_requester or has_permission):
            await interaction.followup.send(embed=create_error_embed(
                "You can only cancel your own swap requests, or you need officer permission."
            ))
            return
        
        # Cancel the request
        await self.db.update_swap_request_status(request_id, "cancelled")
        
        await interaction.followup.send(embed=create_success_embed(
            f"Swap request #{request_id} has been cancelled."
        ))
        
        logger.info(f"Swap #{request_id} cancelled by {interaction.user}")
    
    @app_commands.command(name="swap_status", description="View your active swap requests")
    async def swap_status(self, interaction: discord.Interaction):
        """View your active swap requests.
        
        Args:
            interaction: Discord interaction
        """
        await interaction.response.defer()
        
        # Get player
        player = await self.db.get_player_by_discord_id(str(interaction.user.id))
        if not player:
            await interaction.followup.send(embed=create_error_embed(
                "You are not registered. Ask an officer to add you with `/player_add`."
            ))
            return
        
        # Get player's swap requests
        swap_requests = await self.db.get_player_swap_requests(player.player_id)
        
        if not swap_requests:
            await interaction.followup.send(embed=create_success_embed(
                "You have no swap requests."
            ))
            return
        
        # Create embed
        embed = discord.Embed(
            title=f"🔄 Swap Requests for {player.player_name}",
            color=0x5865F2
        )
        
        all_players = await self.db.get_all_players()
        all_raids = await self.db.get_all_raids()
        
        for swap_request in swap_requests[:10]:  # Limit to 10
            raid = next((r for r in all_raids if r.raid_id == swap_request.raid_id), None)
            
            if raid:
                value = f"**Raid:** {raid.raid_date}\n"
                value += f"**Status:** {swap_request.status}\n"
                
                if swap_request.reason:
                    value += f"**Reason:** {swap_request.reason}\n"
                
                if swap_request.accepting_player_id:
                    accepting_player = next((p for p in all_players if p.player_id == swap_request.accepting_player_id), None)
                    if accepting_player:
                        value += f"**Accepted by:** {accepting_player.player_name}\n"
                
                embed.add_field(
                    name=f"Request #{swap_request.request_id}",
                    value=value,
                    inline=False
                )
        
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot, db: Database):
    """Setup function to add cog to bot.
    
    Args:
        bot: Discord bot instance
        db: Database instance
    """
    await bot.add_cog(SwapCommands(bot, db))
