"""Discord embed builders for various bot responses."""
import discord
from typing import List, Tuple
from database.models import Player, Raid, RosterAssignment
from .constants import WOW_CLASS_COLORS, DEFAULT_EMBED_COLOR, ERROR_EMBED_COLOR, SUCCESS_EMBED_COLOR


def create_error_embed(message: str) -> discord.Embed:
    """Create an error embed.
    
    Args:
        message: Error message
        
    Returns:
        Discord embed
    """
    embed = discord.Embed(
        title="❌ Error",
        description=message,
        color=ERROR_EMBED_COLOR
    )
    return embed


def create_success_embed(message: str) -> discord.Embed:
    """Create a success embed.
    
    Args:
        message: Success message
        
    Returns:
        Discord embed
    """
    embed = discord.Embed(
        title="✅ Success",
        description=message,
        color=SUCCESS_EMBED_COLOR
    )
    return embed


def create_roster_embed(raid: Raid, roster_data: List[Tuple[RosterAssignment, Player, str]]) -> discord.Embed:
    """Create a roster display embed.
    
    Args:
        raid: Raid object
        roster_data: List of (RosterAssignment, Player, class_name) tuples
        
    Returns:
        Discord embed
    """
    # Create title
    title = f"📋 Raid Roster - {raid.raid_date}"
    if raid.raid_time:
        title += f" at {raid.raid_time}"
    if raid.timezone:
        title += f" {raid.timezone}"
    
    embed = discord.Embed(
        title=title,
        color=DEFAULT_EMBED_COLOR
    )
    
    # Separate roster by status
    main_roster = []
    benches = []
    absences = []
    swaps = []
    
    for assignment, player, class_name in roster_data:
        entry = f"{player.player_name} ({assignment.character_name})"
        
        if assignment.status == "main":
            main_roster.append((entry, class_name))
        elif assignment.status == "bench":
            benches.append((entry, class_name))
        elif assignment.status == "absent":
            absences.append((entry, class_name))
        elif assignment.status == "swap":
            swaps.append((entry, class_name))
    
    # Add main roster section
    if main_roster:
        roster_text = "\n".join([f"• {entry}" for entry, _ in main_roster])
        embed.add_field(
            name=f"Main Roster ({len(main_roster)})",
            value=roster_text if roster_text else "Empty",
            inline=False
        )
    
    # Add benches section
    if benches:
        bench_text = "\n".join([f"• {entry}" for entry, _ in benches])
        embed.add_field(
            name=f"Benches ({len(benches)})",
            value=bench_text,
            inline=False
        )
    
    # Add absences section
    if absences:
        absence_text = "\n".join([f"• {entry}" for entry, _ in absences])
        embed.add_field(
            name=f"Absences ({len(absences)})",
            value=absence_text,
            inline=False
        )
    
    # Add swaps section
    if swaps:
        swap_text = "\n".join([f"• {entry}" for entry, _ in swaps])
        embed.add_field(
            name=f"Swaps ({len(swaps)})",
            value=swap_text,
            inline=False
        )
    
    if not roster_data:
        embed.description = "No players assigned yet."
    
    return embed


def create_player_stats_embed(player: Player, characters: list) -> discord.Embed:
    """Create a player statistics embed.
    
    Args:
        player: Player object
        characters: List of Character objects
        
    Returns:
        Discord embed
    """
    embed = discord.Embed(
        title=f"📊 Stats for {player.player_name}",
        color=DEFAULT_EMBED_COLOR
    )
    
    embed.add_field(
        name="Raids Rostered",
        value=str(player.total_raids_rostered),
        inline=True
    )
    
    embed.add_field(
        name="Total Benches",
        value=str(player.total_benches),
        inline=True
    )
    
    # Add characters
    if characters:
        char_list = "\n".join([
            f"• {char.character_name} ({char.class_name}{f' - {char.role}' if char.role else ''})"
            for char in characters
        ])
        embed.add_field(
            name="Characters",
            value=char_list,
            inline=False
        )
    else:
        embed.add_field(
            name="Characters",
            value="No characters registered",
            inline=False
        )
    
    return embed


def create_player_list_embed(players: List[Player]) -> discord.Embed:
    """Create a player list embed.
    
    Args:
        players: List of Player objects
        
    Returns:
        Discord embed
    """
    embed = discord.Embed(
        title="👥 Registered Players",
        color=DEFAULT_EMBED_COLOR
    )
    
    if not players:
        embed.description = "No players registered yet."
        return embed
    
    # Split into chunks if there are many players
    player_text = "\n".join([
        f"• **{player.player_name}** - Raids: {player.total_raids_rostered}, Benches: {player.total_benches}"
        for player in players[:25]  # Limit to 25 to avoid embed limits
    ])
    
    embed.description = player_text
    
    if len(players) > 25:
        embed.set_footer(text=f"Showing 25 of {len(players)} players")
    
    return embed


def create_raid_list_embed(raids: List[Raid]) -> discord.Embed:
    """Create a raid list embed.
    
    Args:
        raids: List of Raid objects
        
    Returns:
        Discord embed
    """
    embed = discord.Embed(
        title="📅 Upcoming Raids",
        color=DEFAULT_EMBED_COLOR
    )
    
    if not raids:
        embed.description = "No raids scheduled yet."
        return embed
    
    raid_text = "\n".join([
        f"• **{raid.raid_date}**{f' at {raid.raid_time}' if raid.raid_time else ''}{f' {raid.timezone}' if raid.timezone else ''}"
        for raid in raids[:25]  # Limit to 25
    ])
    
    embed.description = raid_text
    
    if len(raids) > 25:
        embed.set_footer(text=f"Showing 25 of {len(raids)} raids")
    
    return embed


def create_overview_stats_embed(total_players: int, total_raids: int, 
                                total_assignments: int) -> discord.Embed:
    """Create overview statistics embed.
    
    Args:
        total_players: Total number of players
        total_raids: Total number of raids
        total_assignments: Total number of roster assignments
        
    Returns:
        Discord embed
    """
    embed = discord.Embed(
        title="📊 Guild Overview",
        color=DEFAULT_EMBED_COLOR
    )
    
    embed.add_field(name="Total Players", value=str(total_players), inline=True)
    embed.add_field(name="Total Raids", value=str(total_raids), inline=True)
    embed.add_field(name="Total Assignments", value=str(total_assignments), inline=True)
    
    return embed
