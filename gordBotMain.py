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
    print(ranks)
    print(na_leaderboard)
    print(eu_leaderboard)
    print(hero)
    print(f'Initialization Complete.')
   
        
users = {"Dregley" : 1165359771, "Jack" : 436326420, "Gord" : 311616544, "Durk" : 336921993,
         "Gfreek" : 108601750, "Fraud" : 1845301134, "BigSqueep" : 1843363705, "CardboardBox" : 190690317,
         'eido' : 1676299122, 'crayon' : 84379844, 'duck' : 7100261, 'deathy' : 87624911, 'mikaels' : 385814004,
         'nkd' : 34262576, 'jonas' : 74963221, 'pkmk' : 179489990, 'eu?guy' : 901357991, 'pct' : 84801726,
         'thirkl' : 105263588, 'ninja':1140097740}

@bot.command()
async def live(ctx, arg):
    df_players = getActive.getLive(users[arg])
    if df_players.empty:
        await ctx.send('Player is not in an active game retard!')
    else:
        msg = await ctx.send('Fetching players in game...')
        team1 = webScraper.getProfiles(df_players, ranks, na_leaderboard, eu_leaderboard, hero)
        await msg.edit(content='PLAYERS IN GAME:')
        #for name in names:
         #   await ctx.send(embed=name)
        await ctx.send(embed=team1)
        #await ctx.send(embed=team2)
        msg2 = await ctx.send('Fetching live streams...')
        lives = webScraper.getTwitchLive(df_players.get('link'))
        if not lives:   
            await msg2.edit(content='No one is streaming this dog ass lobby')
        else:
            await msg2.edit(content='LIVE STREAMS:')
            await ctx.send('\n'.join(lives))

@bot.command()
@commands.is_owner()
async def shutdown(ctx):
    exit()

mov = 'https://www.youtube.com/watch?v=fZ1OGXxb6PM'
gord = 'https://tracklock.gg/players/311616544'
dreg = 'https://tracklock.gg/players/116535977'
ev =  'https://tracklock.gg/players/190690317'
names = [gord, dreg]



@bot.command()
async def test(ctx):
    embedLst =[]
    embed = discord.Embed(title="Team1", url=mov)
    embed.add_field(name='Lady Geist', value='[Mawty Maw]('+gord+')', inline=False)
    embed.add_field(name='Seven', value='[Worst Deadlock Player]('+dreg+')', inline=False)
    
    embedLst.append(embed)
    
    embed1 = discord.Embed(title="Team2")
    embed1.add_field(name='Shiv', value='[Cardboard Box]('+ev+')', inline=False)
    embedLst.append(embed1)
    print(embedLst)
    await ctx.send(embeds=embedLst)

bot.run(os.environ.get('DISCORD_BOT_TOKEN'))