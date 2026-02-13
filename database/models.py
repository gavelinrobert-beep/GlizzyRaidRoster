"""Database models for the raid roster bot."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Player:
    """Represents a player in the system."""
    player_id: Optional[int]
    discord_id: str
    player_name: str
    total_raids_rostered: int = 0
    total_benches: int = 0
    created_at: Optional[datetime] = None


@dataclass
class Character:
    """Represents a character owned by a player."""
    character_id: Optional[int]
    player_id: int
    character_name: str
    class_name: str
    role: Optional[str] = None


@dataclass
class Raid:
    """Represents a raid event."""
    raid_id: Optional[int]
    raid_date: str
    raid_time: Optional[str] = None
    timezone: str = "Server Time"
    created_at: Optional[datetime] = None


@dataclass
class RosterAssignment:
    """Represents a player's assignment to a raid."""
    assignment_id: Optional[int]
    raid_id: int
    player_id: int
    character_name: str
    position: Optional[int] = None
    status: str = "main"  # main, bench, absent, swap


@dataclass
class SwapRequest:
    """Represents a swap request between players."""
    request_id: Optional[int]
    raid_id: int
    requesting_player_id: int
    accepting_player_id: Optional[int] = None
    reason: Optional[str] = None
    status: str = "pending"  # pending, accepted, approved, denied, cancelled
    created_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
