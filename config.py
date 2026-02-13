"""Configuration management for the Discord bot."""
import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for bot settings."""
    
    DISCORD_TOKEN: str = os.getenv("DISCORD_TOKEN", "")
    GUILD_ID: int = int(os.getenv("GUILD_ID", "0"))
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "database/raid_roster.db")
    AUTHORIZED_ROLES: List[str] = os.getenv("AUTHORIZED_ROLES", "Officer,Raid Leader").split(",")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that required configuration is present.
        
        Returns:
            bool: True if configuration is valid, False otherwise
        """
        if not cls.DISCORD_TOKEN:
            print("ERROR: DISCORD_TOKEN not set in .env file")
            return False
        if cls.GUILD_ID == 0:
            print("ERROR: GUILD_ID not set in .env file")
            return False
        return True
