import discord
from discord.ext import commands
import sqlite3

# Database setup
conn = sqlite3.connect('roster.db')
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS players (character_name TEXT PRIMARY KEY, class TEXT, spec_role TEXT)')
conn.commit()

# Bot setup
bot = commands.Bot(command_prefix='/')

@bot.slash_command(name='signup', description='Sign up as a player for the raid')
async def signup(ctx, character_name: str, player_class: str, spec_role: str):
    c.execute('SELECT * FROM players WHERE character_name = ?', (character_name,))
    if c.fetchone() is not None:
        await ctx.respond(f"Character `{character_name}` is already signed up!")
        return

    c.execute('INSERT INTO players (character_name, class, spec_role) VALUES (?, ?, ?)', 
              (character_name, player_class, spec_role))
    conn.commit()
    await ctx.respond(f"Successfully signed up `{character_name}` with class `{player_class}` and role `{spec_role}`!")

# Run the bot
bot.run('YOUR_BOT_TOKEN')