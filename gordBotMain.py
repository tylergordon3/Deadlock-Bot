import discord
import os
from dotenv import load_dotenv
import getActive
import json
import webScraper
from discord.ext import commands
import pandas as pd
import initialize

load_dotenv()


intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='$', intents=intents)

ranks, na_leaderboard, eu_leaderboard, hero = initialize.init()


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    print(hero)
   
users = {"Dregley" : 1165359771, "Jack" : 436326420, "Gord" : 311616544, "Durk" : 336921993,
         "Gfreek" : 108601750, "Fraud" : 1845301134, "BigSqueep" : 1843363705, "CardboardBox" : 190690317,
         'eido' : 1676299122, 'crayon' : 84379844, 'duck' : 7100261, 'deathy' : 87624911, 'mikaels' : 385814004,
         'nkd' : 34262576, 'jonas' : 74963221, 'pkmk' : 179489990, 'eu?guy' : 901357991, 'pct' : 84801726,
         'thirkl' : 105263588, 'ninja':1140097740, 'donut':901186671, 'lystic':97533101}

@bot.command()
async def live(ctx, arg):
    df_players = getActive.getLive(users[arg])
    print(df_players)
    if df_players.empty:
        await ctx.send('Player is not in an active game!')
    else:
        msg = await ctx.send('Fetching players in game...')
        team1, team2 = webScraper.getProfiles(df_players, ranks, na_leaderboard, eu_leaderboard, hero)
        await msg.edit(content='PLAYERS IN GAME:')
        await ctx.send("----------------------------------- TEAM 1 -----------------------------------")
        await ctx.send(embeds=team1)
        await ctx.send("----------------------------------- TEAM 2 -----------------------------------")
        await ctx.send(embeds=team2)
        msg2 = await ctx.send('Fetching live streams...')
        lives = webScraper.getTwitchLive(df_players.get('link'))
        if not lives:   
            await msg2.edit(content='No one is streaming in this lobby.')
        else:
            await msg2.edit(content="----------------------------------- LIVESTREAMS -----------------------------------")
            await ctx.send('\n'.join(lives))

@bot.command()
@commands.is_owner()
async def shutdown(ctx):
    exit()

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if "massive" in message.content.lower():
        await message.channel.send('You know what else is massive?')

    if "low" in message.content.lower():
        await message.channel.send('Just got a lowwwww taper fade.')

bot.run(os.environ.get('DISCORD_BOT_TOKEN'))