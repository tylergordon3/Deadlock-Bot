import discord
import live
import webScraper
from discord.ext import commands
import pandas as pd
import initialize

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
#client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='$', intents=intents)

ranks, leaderboard, hero = initialize.init()


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    print(ranks)
    print(leaderboard)
    print(hero)
    print(f'Initialization Complete.')
   
        
users = {"Dregley" : 1165359771, "Jack" : 436326420, "Gord" : 311616544, "Durk" : 336921993,
         "Gfreek" : 108601750, "Fraud" : 1845301134, "BigSqueep" : 1843363705, "CardboardBox" : 190690317,
         'eido' : 1676299122, 'crayon' : 84379844, 'duck' : 7100261, 'deathy' : 87624911, 'mikaels' : 385814004,
         'nkd' : 34262576}
'''
@bot.command()
async def img(ctx):
    print(f'Sending images')
    embedTest = discord.Embed()
    embedTest.set_image(url=ranks['images'][9]['small_subrank2_webp'])
    await ctx.send(embed = embedTest)'''


@bot.command()
async def liveMatch(ctx, arg):
    user_id = live.fetchLive(users[arg])
    if not user_id:
        await ctx.send('Player is not in an active game retard!')
    else:
        msg = await ctx.send('Fetching players in game...')
        names = webScraper.getProfiles(user_id, ranks, leaderboard, hero)
        await msg.edit(content='PLAYERS IN GAME:')
        for name in names:
            await ctx.send(embed=name)
        msg2 = await ctx.send('Fetching live streams...')
        lives = webScraper.getTwitchLive(user_id)
        if not lives:   
            await msg2.edit(content='No one is streaming this dog ass lobby')
        else:
            await msg2.edit(content='LIVE STREAMS:')
            await ctx.send('\n'.join(lives))

@bot.command()
@commands.is_owner()
async def shutdown(ctx):
    exit()
            
            
   

            












bot.run('MTMzNDY4MzQyNTk5MDI1MDU3Ng.G040FA.awgUHPj7O2gkOg_qb0q6cZCP3FYk0GSgzlAceg')