import discord
import datetime as dt
from discord.ext import commands
from dotenv import load_dotenv
import os
import tools.reqData as rd

load_dotenv()
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
guild_id = [546868043838390299]


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

async def checkDataLastUpd(threshold_hrs = 12):
    last = os.stat('dataDaily/NAmerica.json').st_mtime

    last_datetime = dt.datetime.fromtimestamp(last)
    curr_datetime = dt.datetime.now()

    diff = curr_datetime - last_datetime

    threshold_min = threshold_hrs * 60
   
    return (diff.total_seconds()/60) > threshold_min

async def setup_hook():
    print(f'We have logged in as {bot.user}')
    await load_cogs(bot)
    try:
        bot.tree.copy_global_to(guild=discord.Object(id=guild_id[0]))
        sync = await bot.tree.sync(guild=discord.Object(id=guild_id[0]))
        print(f"Synched {len(sync)} command(s)")
    except Exception as e:
        print(e)
    if (await checkDataLastUpd(1)):
       rd.get_daily()


bot.setup_hook = setup_hook

try:
    bot.run(os.environ.get('DISCORD_BOT_TOKEN'))
except Exception as e:
    print(f"Error when logging in: {e}")   
    