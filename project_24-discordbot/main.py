import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure bot intents
intents = discord.Intents.default()
intents.message_content = True  # Required for message content
intents.members = True         # Required for member-related events
intents.presences = True       # Required for presence info

# Initialize bot
bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    case_insensitive=True,
    help_command=None
)

# --- Events ---
@bot.event
async def on_ready():
    """Called when bot is logged in"""
    print(f"\nBot is ready! Logged in as {bot.user.name}")
    print(f"Guilds: {len(bot.guilds)}")
    print(f"Users: {len(bot.users)}\n")
    await bot.change_presence(activity=discord.Game(name="!help"))

@bot.event
async def on_command_error(ctx, error):
    """Handle command errors"""
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Command not found. Try !help")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing argument: {error.param.name}")
    else:
        await ctx.send(f"⚠️ An error occurred: {str(error)}")

# --- Basic Commands ---
@bot.command()
async def ping(ctx):
    """Check bot latency"""
    latency = round(bot.latency * 1000)
    await ctx.send(f"🏓 Pong! {latency}ms")

@bot.command()
async def hello(ctx):
    """Greet the user"""
    await ctx.send(f"👋 Hello {ctx.author.mention}!")

@bot.command()
async def echo(ctx, *, message: str):
    """Repeat a message"""
    if len(message) > 200:
        await ctx.send("❌ Message too long (max 200 chars)")
        return
    await ctx.send(f"{ctx.author.name} says: {message}")

# --- Help Command ---
@bot.command()
async def help(ctx):
    """Show all commands"""
    embed = discord.Embed(
        title="Bot Commands Help",
        color=discord.Color.blue()
    )
    
    for cmd in bot.commands:
        embed.add_field(
            name=f"!{cmd.name}",
            value=cmd.help or "No description",
            inline=False
        )
    
    await ctx.send(embed=embed)

# --- Run the Bot ---
if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_TOKEN")
    
    if not TOKEN:
        print("Error: No token found in .env file")
        exit(1)
    
    try:
        print("Starting bot...")
        bot.run(TOKEN)
    except discord.LoginFailure:
        print("Error: Invalid bot token. Please check your .env file")
    except discord.PrivilegedIntentsRequired:
        print("Error: Enable 'Presence Intent' and 'Server Members Intent' in Developer Portal")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")