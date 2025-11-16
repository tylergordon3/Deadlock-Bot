from discord.ext import commands, tasks
import os
import tools.reqData as rd
import datetime as dt

guild_id = 1320225481500659752


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # self.odysseyCountdown.start()

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

    @commands.command()
    async def name(self, ctx):
        steve = 549708233640509442
        guild = await self.bot.fetch_guild(guild_id)
        steve_ob = await guild.fetch_member(steve)

        release = "2026/07/17"
        releaseDt = dt.datetime.strptime(release, "%Y/%m/%d")
        now = dt.datetime.now()
        diff = (releaseDt - now).days
        await steve_ob.edit(nick=str(diff))

    @tasks.loop(hours=12)
    async def odysseyCountdown(self):
        steve = 549708233640509442
        guild = await self.bot.fetch_guild(guild_id)
        steve_ob = await guild.fetch_member(steve)

        release = "2026/07/17"
        releaseDt = dt.datetime.strptime(release, "%Y/%m/%d")
        now = dt.datetime.now()
        diff = (releaseDt - now).days
        await steve_ob.edit(nick=str(diff))


async def setup(bot):
    await bot.add_cog(Admin(bot))
