# Changelog

All notable changes to GlizzyRaidRoster will be documented in this file.

## [1.0.0] - 2024-02-13

### Initial Release

#### Added
- **Discord Bot Core**
  - Discord.py integration with slash commands
  - Async/await architecture for optimal performance
  - Comprehensive error handling and logging
  - Configuration management via .env file
  - Auto-syncing of slash commands to Discord

- **Database System**
  - SQLite database with four main tables (players, characters, raids, roster_assignments)
  - Async database operations with aiosqlite
  - Automatic database initialization from SQL schema
  - Foreign key constraints for data integrity
  - Indexes for query performance
  - Data models with type hints

- **Player Management Commands**
  - `/player_add` - Register new players linked to Discord accounts
  - `/player_addchar` - Add characters with WoW class and role
  - `/player_stats` - View player statistics and characters
  - `/player_list` - List all registered players

- **Roster Management Commands**
  - `/roster_create` - Create raid events with date, time, and timezone
  - `/roster_add` - Add players to main roster
  - `/roster_remove` - Remove players from roster
  - `/roster_bench` - Move players to bench
  - `/roster_absence` - Mark players as absent
  - `/roster_swap` - Record swaps between players
  - `/roster_view` - Display formatted roster with embeds
  - `/roster_list` - List all upcoming raids

- **Statistics Commands**
  - `/stats_player` - Detailed player statistics
  - `/stats_overview` - Guild-wide overview statistics

- **Utilities**
  - WoW class color constants (12 classes with official hex colors)
  - Date validator with flexible format support (YYYY-MM-DD, DD/MM/YYYY, natural language)
  - Class and role validators with case-insensitive matching
  - Discord embed builders with color-coded displays
  - Input validation for player and character names

- **Documentation**
  - Comprehensive README with installation guide
  - Quick Start Guide for 5-minute setup
  - Usage Guide with example workflows
  - Troubleshooting section
  - Development guide for contributors
  - Example .env file with all configuration options

- **Quality Assurance**
  - Python type hints throughout codebase
  - Docstrings for all functions and classes
  - Modular code structure
  - Logging for debugging and audit trail
  - Security review with CodeQL (0 vulnerabilities)
  - Code review addressing performance and clarity issues

#### Features
- Support for 12 WoW classes with official color coding
- Flexible date input supporting multiple formats
- Player statistics tracking (raids rostered, benches)
- Multiple characters per player
- Raid roster status management (main/bench/absent/swap)
- Beautiful Discord embeds with rich formatting
- Role-based permissions system (configurable authorized roles)
- Automatic database backup on startup
- Comprehensive error messages

#### Technical Details
- Python 3.8+ compatible
- Dependencies: discord.py, aiosqlite, python-dotenv, python-dateutil
- SQLite for persistent storage
- Async/await for all database operations
- Modular architecture with separate packages for commands, database, and utilities
- Clean separation of concerns (MVC-like pattern)

#### Testing
- Syntax validation for all Python files
- Import verification
- Database operation testing
- Validator testing with edge cases
- Embed creation testing
- Comprehensive integration test suite

### Security
- No hardcoded credentials
- Environment variable configuration
- SQL injection prevention via parameterized queries
- Input validation on all user inputs
- CodeQL security analysis passed

### Performance
- Optimized database queries with indexes
- Efficient count queries for statistics
- Async operations prevent blocking
- Connection pooling via aiosqlite

## [Unreleased]

### Planned Features
- Permission checks based on Discord roles
- Automatic statistics updates when rosters are finalized
- Export roster to text format
- Backup and restore functionality
- Web dashboard for roster visualization
- Integration with WoW API for character validation
- Automated reminders for upcoming raids
- Historical raid tracking and analytics

---

## Version Format

This project follows [Semantic Versioning](https://semver.org/):
- MAJOR version for incompatible API changes
- MINOR version for added functionality (backwards compatible)
- PATCH version for backwards compatible bug fixes

## Categories

- **Added**: New features
- **Changed**: Changes to existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security improvements
