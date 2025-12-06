import asyncio
import json
import discord
from discord.ext import commands

# -----------------------------
# yt-dlp subprocess helper
# -----------------------------

async def extract_audio_url(url: str) -> dict:
    process = await asyncio.create_subprocess_exec(
        "yt-dlp",
        "-f", "bestaudio",
        "-J",
        "--no-playlist",
        url,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        raise RuntimeError(stderr.decode())

    return json.loads(stdout)


# -----------------------------
# Music Cog
# -----------------------------

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = {}

    def get_queue(self, guild_id):
        return self.queue.setdefault(guild_id, [])

    async def ensure_voice(self, ctx):
        if not ctx.author.voice:
            await ctx.send("❗ Join a voice channel first.")
            raise commands.CommandError()

        channel = ctx.author.voice.channel

        if ctx.voice_client:
            if ctx.voice_client.channel != channel:
                await ctx.voice_client.move_to(channel)
            return ctx.voice_client

        return await channel.connect()
    
    @commands.command()
    async def skip(self, ctx):
        vc = ctx.voice_client

        if not vc or not vc.is_playing():
            return await ctx.send("❌ Nothing is playing.")

        vc.stop()
        await ctx.send("⏭ **Skipped.**")

    @commands.command()
    async def queue(self, ctx):
        queue = self.get_queue(ctx.guild.id)

        if not queue:
            return await ctx.send("📭 Queue is empty.")

        msg = "\n".join(
            f"{i+1}. {title}" for i, (title, _) in enumerate(queue)
        )

        await ctx.send(f"📜 **Queue:**\n{msg}")

    # -----------------------------
    # Play command (YouTube URLs)
    # -----------------------------
    async def play_next(self, ctx):
        queue = self.get_queue(ctx.guild.id)

        if not queue:
            return

        title, stream_url = queue.pop(0)

        source = discord.FFmpegPCMAudio(
            stream_url,
            before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            options="-vn",
        )

        ctx.voice_client.play(
            source,
            after=lambda e: self.bot.loop.create_task(
                self.play_next(ctx)
            )
        )

        await ctx.send(f"▶️ **Now playing:** {title}")

    @commands.command()
    async def play(self, ctx, *, url: str):
        vc = await self.ensure_voice(ctx)
        queue = self.get_queue(ctx.guild.id)

        await ctx.send("🔍 Fetching audio…")

        info = await extract_audio_url(url)
        stream_url = info["url"]
        title = info.get("title", "Unknown")

        track = (title, stream_url)

        # ✅ If something is already playing → queue it
        if vc.is_playing():
            queue.append(track)
            return await ctx.send(f"➕ **Queued:** {title}")
        
        source = discord.FFmpegPCMAudio(
            stream_url,
            before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            options="-vn",
        )

        vc.play(
            source,
            after=lambda e: self.bot.loop.create_task(
                self.play_next(ctx)
        ))
        await ctx.send(f"▶️ **Now playing:** {title}")

    # -----------------------------
    # Stop / Leave
    # -----------------------------

    @commands.command()
    async def stop(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("🛑 Disconnected.")
        else:
            await ctx.send("Not connected.")


async def setup(bot):
    await bot.add_cog(Music(bot))
