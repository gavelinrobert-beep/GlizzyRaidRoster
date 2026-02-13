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
6. **Use visual calendar**: Generate roster calendars weekly for easy overview

## Visual Roster Calendar

### Generating a Roster Calendar

Create a beautiful visual calendar showing upcoming raids:

```
/roster_calendar weeks:4
```

This generates an image showing:
- All players in rows with their stats (raids rostered/benches)
- Each raid date in columns
- Color-coded cells by WoW class for main roster
- Darker colors for bench players
- Red tint for absences
- Orange tint for swaps

The calendar provides an at-a-glance view similar to Google Sheets, making it easy to:
- See who's rostered across multiple raids
- Identify patterns in player availability
- Plan rotations and balance bench time
- Share with the guild for transparency

**Example:**
```
/roster_calendar weeks:2  # Show next 2 weeks
/roster_calendar weeks:8  # Show next 2 months
```

### When to Use Calendar View

- **Weekly planning**: Generate at the start of each week
- **Officer meetings**: Review roster balance across raids
- **Guild announcements**: Share the visual in a roster channel
- **Long-term planning**: See patterns over multiple weeks

## Swap Request System

The swap system allows main roster players to request swaps with bench players, streamlining the process and reducing officer workload.

### Player-Initiated Swap Requests

**As a Main Roster Player:**

If you can't make a raid, request a swap:
```
/swap_request raid_date:2024-02-19 reason:Family emergency
```

This creates a swap request that bench players can see and accept.

**As a Bench Player:**

View pending swap requests:
```
/swap_list
```

Accept a swap request to take the main roster spot:
```
/swap_accept request_id:1
```

**Check Your Swap Status:**
```
/swap_status
```

### Officer Management of Swaps

**View All Pending Swaps:**
```
/swap_list
```

**Approve a Swap:**
```
/swap_approve request_id:1
```

This executes the swap:
- Requesting player moves to bench
- Accepting player moves to main roster
- Both players' statistics are updated
- Both players are notified

**Deny a Swap:**
```
/swap_deny request_id:1 reason:Roster comp needs
```

**Cancel Any Swap:**
```
/swap_cancel request_id:1
```

### Swap Request Workflow

1. **Request Created**: Main roster player uses `/swap_request`
2. **Notification Sent**: System notifies bench players (if SWAP_CHANNEL_ID is set)
3. **Bench Player Accepts**: Bench player uses `/swap_accept`
4. **Auto-Approve or Manual Review**:
   - If `AUTO_APPROVE_SWAPS=true`: Swap executes immediately
   - If `AUTO_APPROVE_SWAPS=false`: Officers must approve with `/swap_approve`
5. **Swap Executed**: Roster assignments are swapped, stats updated

### Configuration Options

In your `.env` file:

```env
# Channel where swap notifications are sent (0 to disable)
SWAP_CHANNEL_ID=123456789

# Auto-approve swaps without officer review (true/false)
AUTO_APPROVE_SWAPS=false

# Hours before swap requests expire
SWAP_REQUEST_EXPIRY_HOURS=48
```

**Recommendation:**
- Set `AUTO_APPROVE_SWAPS=true` for high-trust guilds to reduce officer workload
- Set `AUTO_APPROVE_SWAPS=false` for stricter roster control
- Configure `SWAP_CHANNEL_ID` to a dedicated swap-requests channel

### Example Swap Scenarios

**Scenario 1: Emergency Swap**
```
# Player can't make raid
/swap_request raid_date:2024-02-19 reason:Work emergency

# Bench player volunteers
/swap_accept request_id:1

# Officer approves (if manual approval required)
/swap_approve request_id:1
```

**Scenario 2: Checking Swap Status**
```
# Player checks their pending swaps
/swap_status

# Shows all their active swap requests with status
```

**Scenario 3: Canceling a Swap**
```
# Player changes mind
/swap_cancel request_id:1

# Or officer cancels if needed
/swap_cancel request_id:1
```

### Benefits of the Swap System

1. **Player Empowerment**: Players can manage their own availability
2. **Reduced Officer Workload**: Less manual roster management
3. **Transparency**: All swaps are logged and visible
4. **Fair Process**: Bench players can volunteer for open spots
5. **Statistics Tracking**: Swaps properly update player stats
6. **Audit Trail**: All swap history is preserved in the database

## Advanced Usage

### Combining Calendar and Swaps

1. Generate a weekly calendar to share with the guild
2. Players see their assignments and can request swaps if needed
3. Officers review swap requests and approve as needed
4. Regenerate calendar to show updated roster

```
# Monday: Generate calendar for the week
/roster_calendar weeks:1

# Mid-week: Player requests swap
/swap_request raid_date:2024-02-19 reason:Can't make it

# Bench player accepts
/swap_accept request_id:1

# Officer approves
/swap_approve request_id:1

# Friday: Generate updated calendar
/roster_calendar weeks:1
```

### Viewing Swaps in Roster

When viewing a specific raid roster:
```
/roster_view raid_date:2024-02-19
```

The display now includes a "Pending Swaps" section showing any active swap requests for that raid.

## Next Steps

- Explore all available commands
- Set up automatic backups for your database
- Configure swap system settings for your guild's needs
- Customize the bot's permissions for your officers
- Generate weekly roster calendars for guild transparency
- Consider adding custom commands for your guild's specific needs

For more information, see the main [README.md](README.md).
