-- Players table: Stores player information
CREATE TABLE IF NOT EXISTS players (
    player_id INTEGER PRIMARY KEY AUTOINCREMENT,
    discord_id TEXT UNIQUE NOT NULL,
    player_name TEXT NOT NULL,
    total_raids_rostered INTEGER DEFAULT 0,
    total_benches INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Characters table: Stores character information for each player
CREATE TABLE IF NOT EXISTS characters (
    character_id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL,
    character_name TEXT NOT NULL,
    class TEXT NOT NULL,
    role TEXT,
    FOREIGN KEY (player_id) REFERENCES players(player_id) ON DELETE CASCADE,
    UNIQUE(player_id, character_name)
);

-- Raids table: Stores raid event information
CREATE TABLE IF NOT EXISTS raids (
    raid_id INTEGER PRIMARY KEY AUTOINCREMENT,
    raid_date TEXT NOT NULL,
    raid_time TEXT,
    timezone TEXT DEFAULT 'Server Time',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(raid_date)
);

-- Roster assignments table: Stores player assignments for each raid
CREATE TABLE IF NOT EXISTS roster_assignments (
    assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    raid_id INTEGER NOT NULL,
    player_id INTEGER NOT NULL,
    character_name TEXT NOT NULL,
    position INTEGER,
    status TEXT DEFAULT 'main',
    FOREIGN KEY (raid_id) REFERENCES raids(raid_id) ON DELETE CASCADE,
    FOREIGN KEY (player_id) REFERENCES players(player_id) ON DELETE CASCADE,
    UNIQUE(raid_id, player_id)
);

-- Swap requests table: Stores swap requests between rostered and bench players
CREATE TABLE IF NOT EXISTS swap_requests (
    request_id INTEGER PRIMARY KEY AUTOINCREMENT,
    raid_id INTEGER NOT NULL,
    requesting_player_id INTEGER NOT NULL,
    accepting_player_id INTEGER,
    reason TEXT,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    FOREIGN KEY (raid_id) REFERENCES raids(raid_id) ON DELETE CASCADE,
    FOREIGN KEY (requesting_player_id) REFERENCES players(player_id) ON DELETE CASCADE,
    FOREIGN KEY (accepting_player_id) REFERENCES players(player_id) ON DELETE CASCADE
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_players_discord_id ON players(discord_id);
CREATE INDEX IF NOT EXISTS idx_characters_player_id ON characters(player_id);
CREATE INDEX IF NOT EXISTS idx_raids_date ON raids(raid_date);
CREATE INDEX IF NOT EXISTS idx_roster_raid_id ON roster_assignments(raid_id);
CREATE INDEX IF NOT EXISTS idx_roster_player_id ON roster_assignments(player_id);
CREATE INDEX IF NOT EXISTS idx_swap_requests_raid_id ON swap_requests(raid_id);
CREATE INDEX IF NOT EXISTS idx_swap_requests_status ON swap_requests(status);
