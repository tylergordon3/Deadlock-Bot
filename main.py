import discord
import datetime as dt
from discord.ext import commands, tasks
from dotenv import load_dotenv
import os
import tools.reqData as rd
import traceback
import asyncio
import subprocess

load_dotenv()
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

SCRIPT_PATH =  "/home/tgordon/cbb-model/deploy.sh"
SCRIPT_CWD = "/home/tgordon/cbb-model"
GUILD_ID = os.environ.get("GUILD_ID")

bot = commands.Bot(command_prefix="/", intents=intents)

async def run_batch():
    def _run():
        return subprocess.run(
            ["/bin/bash", SCRIPT_PATH],
            cwd=SCRIPT_CWD,
            stdin=subprocess.DEVNULL,     # prevent hangs
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

    result = await asyncio.to_thread(_run)

    if result.stdout:
        print("---- DEPLOY STDOUT ----")
        print(result.stdout)

    if result.stderr:
        print("---- DEPLOY STDERR ----")
        print(result.stderr)

    print(f"Deploy exited with code {result.returncode}")


async def scheduler():
    await bot.wait_until_ready()

    print("Running batch immediately on startup")
    await run_batch()

    while not bot.is_closed():
        now = dt.datetime.now()
        print("hourly_task start.")

        await run_batch()

        # Decide interval
        if now.hour >= 17:  # 5 PM+
            sleep_seconds = 20 * 60
        else:
            sleep_seconds = 60 * 60

        await asyncio.sleep(sleep_seconds)

async def load_cogs(bot):
    for file in os.listdir("cogs"):
        if file.endswith(".py"):
            ext = file[:-3]
            try:
                await bot.load_extension(f"cogs.{ext}")
                print(f"Loaded extension '{ext}'")
            except Exception as e:
                exception = f"{type(e).__name__}: {e}"
                error_data = " ".join(
                    traceback.format_exception(type(e), e, e.__traceback__)
                )
                print(f"Error during execution:\n{error_data[:1000]}\n")

async def setup_hook():
    print(f"We have logged in as {bot.user}")

    await load_cogs(bot)

    bot.loop.create_task(scheduler())
    
    try:
        bot.tree.copy_global_to(guild=discord.Object(id=int(GUILD_ID)))
        sync = await bot.tree.sync(guild=discord.Object(id=int(GUILD_ID)))
        print(f"Synched {len(sync)} command(s)")
    except Exception as e:
        print(e)

bot.setup_hook = setup_hook

try:
    bot.run(os.environ.get("DISCORD_BOT_TOKEN"))
except Exception as e:
    print(f"Error when logging in: {e}")