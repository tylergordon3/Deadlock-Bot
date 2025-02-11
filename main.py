import discord

from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

async def load_cogs(bot):
    for file in os.listdir('cogs'):
        if file.endswith(".py"):
            ext = file[:-3]
            try: 
                await bot.load_extension(f"cogs.{ext}")
                print(f"Loaded extension '{ext}'")
            except Exception as e:
                exception = f"{type(e).__name__}: {e}"
                print(f"Failed to load extension {ext}\n{exception}")

async def setup_hook():
    print(f'We have logged in as {bot.user}')
    await load_cogs(bot)
    await bot.tree.sync()
    
bot.setup_hook = setup_hook

try:
    bot.run(os.environ.get('DISCORD_BOT_TOKEN'))
except Exception as e:
    print(f"Error when logging in: {e}")   
    