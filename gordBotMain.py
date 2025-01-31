import discord
import live
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
#client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='$', intents=intents)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')


users = {"Dregley" : 1165359771, "Jack" : 436326420, "Gord" : 311616544, "Durk" : 336921993,
         "Gfreek" : 108601750, "Fraud" : 1845301134, "BigSqueep" : 1843363705, "CardboardBox" : 190690317}

@bot.command()
async def liveMatch(ctx, arg):
    id = live.fetchLive(users[arg])
    if not id:
        await ctx.send('Player is not in an active game retard!')
    else:
        print('\n'.join(id))
        await ctx.send('PLAYERS IN GAME:')
        await ctx.send('\n'.join(id))
        
''''
@bot.command()
async def leaderboard(ctx, hero):
    id = live.fetchLive(chars[hero])
    await ctx.send(id)
'''
'''
#@client.event
#async def on_message(message):
 #   if message.author == client.user:
  #      return

   # if message.content.startswith('/Gold Rush'):
    #    await message.channel.send('Marthaniel Maw')

        
    #if "massive" in message.content:
        await message.channel.send('like that low taper fade meme?')

    if "low" in message.content:
        await message.channel.send('i just got tapered up')

    if message.content.startswith('dl live'):
        await message.channel.send(live.fetchLive(108601750))

    if message.content.startswith('dl leaderboard'):
        await message.channel.send(live.fetchLive(108601750))
        '''
bot.run('MTMzNDY4MzQyNTk5MDI1MDU3Ng.G040FA.awgUHPj7O2gkOg_qb0q6cZCP3FYk0GSgzlAceg')