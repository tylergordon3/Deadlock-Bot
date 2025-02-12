import discord
from discord.ext import commands
import traceback



class ExceptionHandler(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error (self, ctx: commands.Context, error) -> None:
        embed = discord.Embed(title="Error")
        error_data = " ".join(traceback.format_exception(type(error), error, error.__traceback__))
        embed.description = f"Error during execution:\n```py\n{error_data[:2000]}\n```"
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ExceptionHandler(bot))
