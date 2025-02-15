from discord.ext import commands
import os
import tools.reqData as rd

class Admin(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @commands.command()
    async def reload(self, ctx):
        for file in os.listdir('cogs'):
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
        

async def setup(bot):
    await bot.add_cog(Admin(bot))