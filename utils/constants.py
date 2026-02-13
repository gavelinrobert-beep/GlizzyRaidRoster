"""Constants for World of Warcraft classes and other bot constants."""

# WoW class colors (in hex format)
WOW_CLASS_COLORS = {
    "Death Knight": 0xC41F3B,
    "Demon Hunter": 0xA330C9,
    "Druid": 0xFF7D0A,
    "Hunter": 0xABD473,
    "Mage": 0x69CCF0,
    "Monk": 0x00FF96,
    "Paladin": 0xF58CBA,
    "Priest": 0xFFFFFF,
    "Rogue": 0xFFF569,
    "Shaman": 0x0070DE,
    "Warlock": 0x9482C9,
    "Warrior": 0xC79C6E,
}

# Valid WoW classes
VALID_CLASSES = list(WOW_CLASS_COLORS.keys())

# Valid roles
VALID_ROLES = ["Tank", "Healer", "DPS"]

# Valid roster statuses
VALID_STATUSES = ["main", "bench", "absent", "swap"]

# Default embed color (for general messages)
DEFAULT_EMBED_COLOR = 0x5865F2

# Error embed color
ERROR_EMBED_COLOR = 0xFF0000

# Success embed color
SUCCESS_EMBED_COLOR = 0x00FF00
