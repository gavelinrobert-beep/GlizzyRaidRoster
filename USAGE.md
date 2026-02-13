# Example Usage Guide

This guide demonstrates common workflows for using the GlizzyRaidRoster Discord bot.

## Initial Setup

After installing the bot in your Discord server:

1. Create a `.env` file based on `.env.example`
2. Add your Discord bot token and Guild ID
3. Run the bot: `python bot.py`
4. The bot will automatically create the database and sync commands

## Example Workflow: Setting Up Your First Raid

### Step 1: Register Players

First, register your guild members:

```
/player_add name:Thrall discord_user:@User1
/player_add name:Jaina discord_user:@User2
/player_add name:Sylvanas discord_user:@User3
```

### Step 2: Add Characters

Add each player's characters with their classes and roles:

```
/player_addchar player_name:Thrall character_name:ThrallMain wow_class:Shaman role:Healer
/player_addchar player_name:Jaina character_name:JainaFrost wow_class:Mage role:DPS
/player_addchar player_name:Sylvanas character_name:SylvanasHunt wow_class:Hunter role:DPS
```

### Step 3: Create a Raid

Create your raid event:

```
/roster_create date:2024-02-19 time:8:00 PM timezone:EST
```

You can use flexible date formats:
- `date:2024-02-19` (YYYY-MM-DD)
- `date:19/02/2024` (DD/MM/YYYY)
- `date:Feb 19` (natural language)

### Step 4: Build Your Roster

Add players to the raid:

```
/roster_add raid_date:2024-02-19 player_name:Thrall character_name:ThrallMain position:1
/roster_add raid_date:2024-02-19 player_name:Jaina character_name:JainaFrost position:2
/roster_add raid_date:2024-02-19 player_name:Sylvanas character_name:SylvanasHunt position:3
```

### Step 5: View Your Roster

Display the complete roster:

```
/roster_view raid_date:2024-02-19
```

This shows a beautiful embed with:
- Main roster
- Benches
- Absences
- Swaps

## Managing Rosters

### Moving a Player to Bench

```
/roster_bench raid_date:2024-02-19 player_name:Sylvanas
```

### Marking Someone Absent

```
/roster_absence raid_date:2024-02-19 player_name:Jaina
```

### Recording a Swap

```
/roster_swap raid_date:2024-02-19 player1:Thrall player2:Jaina
```

### Removing a Player

```
/roster_remove raid_date:2024-02-19 player_name:Sylvanas
```

## Viewing Statistics

### Individual Player Stats

```
/player_stats player_name:Thrall
```

Shows:
- Total raids rostered
- Total times benched
- All registered characters

### Guild Overview

```
/stats_overview
```

Shows:
- Total registered players
- Total scheduled raids
- Total roster assignments

## Listing Data

### List All Players

```
/player_list
```

### List All Raids

```
/roster_list
```

## Best Practices

1. **Register Players First**: Always add players before creating raids
2. **Add Multiple Characters**: Players can have multiple characters for different roles
3. **Use Consistent Dates**: Stick to one date format for easier management
4. **Regular Updates**: Update rosters as needed using bench/absence commands
5. **Review Before Raid**: Use `/roster_view` to confirm the lineup before raid time

## Common Scenarios

### Scenario: Last-Minute Replacement

Someone can't make it:
```
/roster_absence raid_date:2024-02-19 player_name:Jaina
/roster_add raid_date:2024-02-19 player_name:Sylvanas character_name:SylvanasHunt
```

### Scenario: Role Swap

Need to swap two players' positions:
```
/roster_swap raid_date:2024-02-19 player1:Thrall player2:Jaina
```

### Scenario: Creating Multiple Raids

Planning a raid week:
```
/roster_create date:2024-02-19 time:8:00 PM timezone:EST
/roster_create date:2024-02-20 time:8:00 PM timezone:EST
/roster_create date:2024-02-21 time:8:00 PM timezone:EST
```

### Scenario: Adding an Alt Character

Player has multiple characters:
```
/player_addchar player_name:Thrall character_name:ThrallAlt wow_class:Warrior role:Tank
```

Now Thrall can be assigned with either character:
```
/roster_add raid_date:2024-02-19 player_name:Thrall character_name:ThrallAlt position:1
```

## Troubleshooting Common Issues

### "Player not found"
Make sure you've registered the player first with `/player_add`

### "Raid not found"
Create the raid first with `/roster_create` before adding players

### "Player already assigned"
Each player can only be assigned once per raid. Remove them first if changing their character.

### Commands don't appear
Make sure the bot has proper permissions and `GUILD_ID` is set correctly in `.env`

## Tips for Raid Leaders

1. **Create raids in advance**: Set up your weekly raids at the start of the week
2. **Communicate changes**: Use Discord channels to notify about roster changes
3. **Track statistics**: Use `/stats_overview` to monitor participation
4. **Review benches**: Check player bench counts with `/player_stats` to rotate fairly
5. **Backup your database**: Regularly backup `database/raid_roster.db`

## Next Steps

- Explore all available commands
- Set up automatic backups for your database
- Customize the bot's permissions for your officers
- Consider adding custom commands for your guild's specific needs

For more information, see the main [README.md](README.md).
