import json
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

# Retrieve necessary variables from the environment
GUILD_ID = os.getenv('GUILD_ID')
BOT_TOKEN = os.getenv('BOT_TOKEN')

if not GUILD_ID:
    print("Error: GUILD_ID is not set in the .env file!")
    exit(1)
if not BOT_TOKEN:
    print("Error: BOT_TOKEN is not set in the .env file!")
    exit(1)

GUILD_ID = int(GUILD_ID)

# Dynamically construct the path to lore.json
current_dir = os.path.dirname(os.path.abspath(__file__))
lore_path = os.path.join(current_dir, '..', 'lore.json')  # Adjust path to parent directory

try:
    with open(lore_path, 'r', encoding='utf-8') as file:
        destiny2_characters = json.load(file)
    # Lowercase keys for case-insensitive lookup
    lowercase_lore = {k.lower(): v for k, v in destiny2_characters.items()}
except FileNotFoundError:
    print(f"Error: 'lore.json' file not found at {lore_path}. Please ensure it is in the correct directory.")
    exit(1)

# Helper to safely add fields to embeds
MAX_FIELD_LENGTH = 1024
def safe_add_field(embed, *, name, value, inline=False):
    """Adds a field to the embed, splitting into multiple fields if value is too long."""
    if len(value) <= MAX_FIELD_LENGTH:
        embed.add_field(name=name, value=value, inline=inline)
    else:
        chunks = [value[i:i+MAX_FIELD_LENGTH] for i in range(0, len(value), MAX_FIELD_LENGTH)]
        for idx, chunk in enumerate(chunks):
            field_name = name if idx == 0 else f"{name} (cont.)"
            embed.add_field(name=field_name, value=chunk, inline=inline)

# Initialize the bot with explicit intents
intents = discord.Intents.default()
intents.messages = True  # Allows reading of message content
intents.guilds = True    # Allows access to guild (server) events
intents.message_content = True  # Critical for reading message content for commands

bot = commands.Bot(command_prefix="\\", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
    print(f"{bot.user.name} is online, slash commands are synced, and ready to serve lore!")
    print("by WH33LS")
    activity = discord.Activity(type=discord.ActivityType.watching, name="for lore requests")
    await bot.change_presence(status=discord.Status.online, activity=activity)

# Message-based command for "tell me about"
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Check if the message starts with "tell me about"
    if message.content.lower().startswith("tell me about"):
        character_name = message.content[14:].strip()
        character_data = lowercase_lore.get(character_name.lower())

        if character_data:
            embed = discord.Embed(
                title=f"Lore of {character_name}",
                description=character_data["description"],
                color=discord.Color.green()
            )
            embed.add_field(name="Faction", value=character_data["faction"], inline=True)
            embed.add_field(name="Role", value=character_data["role"], inline=True)
            safe_add_field(embed, name="Key Events", value=", ".join(character_data["key_events"]), inline=False)

            # Add Additional Lore
            additional_lore = character_data.get("additional_lore", {})
            for title, content in additional_lore.items():
                if title == "fireteam":
                    fireteam_details = "\n\n".join(
                        f"**{member}**\nRole: {details['role']}\nFate: {details['fate']}\nReflection: {details['reflection']}"
                        for member, details in content.items()
                    )
                    safe_add_field(embed, name="Fireteam", value=fireteam_details, inline=False)
                elif title == "quotes":
                    quotes = "\n".join(f"\"{quote}\"" for quote in content)
                    safe_add_field(embed, name=title.replace("_", " ").title(), value=quotes, inline=False)
                else:
                    safe_add_field(embed, name=title.replace("_", " ").title(), value=content, inline=False)

            embed.set_footer(text=f"First Appearance: {character_data['first_appearance']}")
            if "image_url" in character_data:
                embed.set_thumbnail(url=character_data["image_url"])

            await message.channel.send(embed=embed)
        else:
            await message.channel.send(f"Sorry, I couldn't find any lore for '{character_name}'. Please check your spelling or try another name!")
    else:
        await bot.process_commands(message)

# Slash command to fetch lore for a specific character (case-insensitive)
@bot.tree.command(name="lore", description="Fetch lore for a specific character!")
async def slash_lore(interaction: discord.Interaction, character_name: str):
    character_data = lowercase_lore.get(character_name.lower())

    if character_data:
        embed = discord.Embed(
            title=f"Lore of {character_name}",
            description=character_data["description"],
            color=discord.Color.blue()
        )
        embed.add_field(name="Faction", value=character_data["faction"], inline=True)
        embed.add_field(name="Role", value=character_data["role"], inline=True)
        safe_add_field(embed, name="Key Events", value=", ".join(character_data["key_events"]), inline=False)

        # Add Additional Lore
        additional_lore = character_data.get("additional_lore", {})
        for title, content in additional_lore.items():
            if title == "fireteam":
                fireteam_details = "\n\n".join(
                    f"**{member}**\nRole: {details['role']}\nFate: {details['fate']}\nReflection: {details['reflection']}"
                    for member, details in content.items()
                )
                safe_add_field(embed, name="Fireteam", value=fireteam_details, inline=False)
            elif title == "quotes":
                quotes = "\n".join(f"\"{quote}\"" for quote in content)
                safe_add_field(embed, name=title.replace("_", " ").title(), value=quotes, inline=False)
            else:
                safe_add_field(embed, name=title.replace("_", " ").title(), value=content, inline=False)

        embed.set_footer(text=f"First Appearance: {character_data['first_appearance']}")
        if "image_url" in character_data:
            embed.set_thumbnail(url=character_data["image_url"])

        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message(
            f"Sorry, I couldn't find any lore for '{character_name}'. Please check your spelling!"
        )

# Error handling for commands
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("It looks like you missed something! Please check your command and try again.")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("I don't recognize that command. Use `\\help` to see what I can do!")
    else:
        await ctx.send("An error occurred. Please try again later.")

# Run the bot
bot.run(BOT_TOKEN)

#by WH33LS
