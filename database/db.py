"""Database connection and query functions."""
import aiosqlite
import logging
from pathlib import Path
from typing import List, Optional, Tuple
from .models import Player, Character, Raid, RosterAssignment

logger = logging.getLogger(__name__)


class Database:
    """Database manager for the raid roster bot."""
    
    def __init__(self, db_path: str):
        """Initialize database manager.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.initialized = False
    
    async def initialize(self):
        """Initialize the database by creating tables if they don't exist."""
        # Ensure database directory exists
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        
        # Read and execute initialization SQL
        init_sql_path = Path(__file__).parent / "init.sql"
        with open(init_sql_path, 'r') as f:
            init_sql = f.read()
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.executescript(init_sql)
            await db.commit()
        
        self.initialized = True
        logger.info(f"Database initialized at {self.db_path}")
    
    # Player operations
    async def add_player(self, discord_id: str, player_name: str) -> Optional[int]:
        """Add a new player to the database.
        
        Args:
            discord_id: Discord user ID
            player_name: Player's name
            
        Returns:
            Player ID if successful, None otherwise
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    "INSERT INTO players (discord_id, player_name) VALUES (?, ?)",
                    (discord_id, player_name)
                )
                await db.commit()
                return cursor.lastrowid
        except aiosqlite.IntegrityError:
            logger.warning(f"Player with discord_id {discord_id} already exists")
            return None
    
    async def get_player_by_discord_id(self, discord_id: str) -> Optional[Player]:
        """Get player by Discord ID.
        
        Args:
            discord_id: Discord user ID
            
        Returns:
            Player object if found, None otherwise
        """
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM players WHERE discord_id = ?",
                (discord_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return Player(
                        player_id=row['player_id'],
                        discord_id=row['discord_id'],
                        player_name=row['player_name'],
                        total_raids_rostered=row['total_raids_rostered'],
                        total_benches=row['total_benches'],
                        created_at=row['created_at']
                    )
        return None
    
    async def get_player_by_name(self, player_name: str) -> Optional[Player]:
        """Get player by name.
        
        Args:
            player_name: Player's name
            
        Returns:
            Player object if found, None otherwise
        """
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM players WHERE player_name = ?",
                (player_name,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return Player(
                        player_id=row['player_id'],
                        discord_id=row['discord_id'],
                        player_name=row['player_name'],
                        total_raids_rostered=row['total_raids_rostered'],
                        total_benches=row['total_benches'],
                        created_at=row['created_at']
                    )
        return None
    
    async def get_all_players(self) -> List[Player]:
        """Get all players from the database.
        
        Returns:
            List of Player objects
        """
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM players ORDER BY player_name") as cursor:
                rows = await cursor.fetchall()
                return [
                    Player(
                        player_id=row['player_id'],
                        discord_id=row['discord_id'],
                        player_name=row['player_name'],
                        total_raids_rostered=row['total_raids_rostered'],
                        total_benches=row['total_benches'],
                        created_at=row['created_at']
                    )
                    for row in rows
                ]
    
    async def update_player_stats(self, player_id: int, raids_rostered: int = 0, benches: int = 0):
        """Update player statistics.
        
        Args:
            player_id: Player ID
            raids_rostered: Number to increment raids rostered by
            benches: Number to increment benches by
        """
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """UPDATE players 
                   SET total_raids_rostered = total_raids_rostered + ?,
                       total_benches = total_benches + ?
                   WHERE player_id = ?""",
                (raids_rostered, benches, player_id)
            )
            await db.commit()
    
    # Character operations
    async def add_character(self, player_id: int, character_name: str, 
                          class_name: str, role: Optional[str] = None) -> Optional[int]:
        """Add a character to a player.
        
        Args:
            player_id: Player ID
            character_name: Character name
            class_name: WoW class name
            role: Character role (optional)
            
        Returns:
            Character ID if successful, None otherwise
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    "INSERT INTO characters (player_id, character_name, class, role) VALUES (?, ?, ?, ?)",
                    (player_id, character_name, class_name, role)
                )
                await db.commit()
                return cursor.lastrowid
        except aiosqlite.IntegrityError:
            logger.warning(f"Character {character_name} already exists for player {player_id}")
            return None
    
    async def get_player_characters(self, player_id: int) -> List[Character]:
        """Get all characters for a player.
        
        Args:
            player_id: Player ID
            
        Returns:
            List of Character objects
        """
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM characters WHERE player_id = ?",
                (player_id,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [
                    Character(
                        character_id=row['character_id'],
                        player_id=row['player_id'],
                        character_name=row['character_name'],
                        class_name=row['class'],
                        role=row['role']
                    )
                    for row in rows
                ]
    
    # Raid operations
    async def create_raid(self, raid_date: str, raid_time: Optional[str] = None, 
                         timezone: str = "Server Time") -> Optional[int]:
        """Create a new raid event.
        
        Args:
            raid_date: Raid date
            raid_time: Raid time (optional)
            timezone: Timezone (default: ST)
            
        Returns:
            Raid ID if successful, None otherwise
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    "INSERT INTO raids (raid_date, raid_time, timezone) VALUES (?, ?, ?)",
                    (raid_date, raid_time, timezone)
                )
                await db.commit()
                return cursor.lastrowid
        except aiosqlite.IntegrityError:
            logger.warning(f"Raid for date {raid_date} already exists")
            return None
    
    async def get_raid_by_date(self, raid_date: str) -> Optional[Raid]:
        """Get raid by date.
        
        Args:
            raid_date: Raid date
            
        Returns:
            Raid object if found, None otherwise
        """
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM raids WHERE raid_date = ?",
                (raid_date,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return Raid(
                        raid_id=row['raid_id'],
                        raid_date=row['raid_date'],
                        raid_time=row['raid_time'],
                        timezone=row['timezone'],
                        created_at=row['created_at']
                    )
        return None
    
    async def get_all_raids(self) -> List[Raid]:
        """Get all raids from the database.
        
        Returns:
            List of Raid objects
        """
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM raids ORDER BY raid_date") as cursor:
                rows = await cursor.fetchall()
                return [
                    Raid(
                        raid_id=row['raid_id'],
                        raid_date=row['raid_date'],
                        raid_time=row['raid_time'],
                        timezone=row['timezone'],
                        created_at=row['created_at']
                    )
                    for row in rows
                ]
    
    # Roster assignment operations
    async def add_roster_assignment(self, raid_id: int, player_id: int, 
                                   character_name: str, position: Optional[int] = None,
                                   status: str = "main") -> Optional[int]:
        """Add a roster assignment.
        
        Args:
            raid_id: Raid ID
            player_id: Player ID
            character_name: Character name
            position: Position in roster (optional)
            status: Assignment status (main, bench, absent, swap)
            
        Returns:
            Assignment ID if successful, None otherwise
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    """INSERT INTO roster_assignments 
                       (raid_id, player_id, character_name, position, status) 
                       VALUES (?, ?, ?, ?, ?)""",
                    (raid_id, player_id, character_name, position, status)
                )
                await db.commit()
                return cursor.lastrowid
        except aiosqlite.IntegrityError:
            logger.warning(f"Player {player_id} already assigned to raid {raid_id}")
            return None
    
    async def update_roster_assignment_status(self, raid_id: int, player_id: int, status: str):
        """Update the status of a roster assignment.
        
        Args:
            raid_id: Raid ID
            player_id: Player ID
            status: New status (main, bench, absent, swap)
        """
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE roster_assignments SET status = ? WHERE raid_id = ? AND player_id = ?",
                (status, raid_id, player_id)
            )
            await db.commit()
    
    async def remove_roster_assignment(self, raid_id: int, player_id: int):
        """Remove a roster assignment.
        
        Args:
            raid_id: Raid ID
            player_id: Player ID
        """
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "DELETE FROM roster_assignments WHERE raid_id = ? AND player_id = ?",
                (raid_id, player_id)
            )
            await db.commit()
    
    async def get_raid_roster(self, raid_id: int) -> List[Tuple[RosterAssignment, Player, str]]:
        """Get the complete roster for a raid with player and character details.
        
        Args:
            raid_id: Raid ID
            
        Returns:
            List of tuples (RosterAssignment, Player, class_name)
        """
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                """SELECT ra.*, p.*, c.class
                   FROM roster_assignments ra
                   JOIN players p ON ra.player_id = p.player_id
                   LEFT JOIN characters c ON p.player_id = c.player_id 
                       AND ra.character_name = c.character_name
                   WHERE ra.raid_id = ?
                   ORDER BY ra.position, p.player_name""",
                (raid_id,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [
                    (
                        RosterAssignment(
                            assignment_id=row['assignment_id'],
                            raid_id=row['raid_id'],
                            player_id=row['player_id'],
                            character_name=row['character_name'],
                            position=row['position'],
                            status=row['status']
                        ),
                        Player(
                            player_id=row['player_id'],
                            discord_id=row['discord_id'],
                            player_name=row['player_name'],
                            total_raids_rostered=row['total_raids_rostered'],
                            total_benches=row['total_benches'],
                            created_at=row['created_at']
                        ),
                        row['class'] or "Unknown"
                    )
                    for row in rows
                ]
    
    async def count_total_assignments(self) -> int:
        """Count total number of roster assignments.
        
        Returns:
            Total count of assignments
        """
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT COUNT(*) FROM roster_assignments") as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0
