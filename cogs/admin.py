from discord.ext import commands, tasks
import os
import tools.reqData as rd
import datetime as dt
import subprocess

guild_id = os.environ.get("GUILD_ID")

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.hourly_deploy.start()

    @commands.command()
    async def reload(self, ctx):
        for file in os.listdir("cogs"):
            if file.endswith(".py"):
                ext = file[:-3]
                try:
                    await self.bot.reload_extension(f"cogs.{ext}")
                    print(f"Reloaded extension '{ext}'")
                except Exception as e:
                    exception = f"{type(e).__name__}: {e}"
                    print(f"Failed to reload extension {ext}\n{exception}")

    @commands.command()
    async def shutdown(self, ctx):
        await ctx.bot.logout()

    @tasks.loop(hours=1)
    async def hourly_deploy(self):
        curr_datetime = dt.datetime.now()
        print(f"Attempting to deploy CBB Website. Time: {curr_datetime}")
        try:
            subprocess.run(
                ["python", r"C:\Users\tmgor\OneDrive\Desktop\deploy.bat"],
                check=True
            )
            print("Script ran successfully")
        except Exception as e:
            print(f"Script failed: {e}")

async def setup(bot):
    await bot.add_cog(Admin(bot))
