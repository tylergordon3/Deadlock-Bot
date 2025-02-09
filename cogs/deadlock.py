import discord
import json

from discord.ext import commands
import tools.initialize as initialize
import pandas as pd


import tools.getData as gd
import tools.useData as ud


ranks, na_leaderboard, eu_leaderboard, hero = initialize.init()

class Deadlock(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.users = gd.load_json('data/users.json')

    @commands.command()
    async def live(self, ctx, arg):
        df_players = gd.getLive(self.users[arg])
        if df_players.empty:
            await ctx.send('Player is not in an active game!')
        else:
            msg = await ctx.send('Fetching players in game...')
            team1, team2 = await ud.getProfiles(df_players, ranks, na_leaderboard, eu_leaderboard, hero)
            await msg.edit(content='PLAYERS IN GAME:')
            await ctx.send("----------------------------------- TEAM 1 -----------------------------------")
            await ctx.send(embeds=team1)
            await ctx.send("----------------------------------- TEAM 2 -----------------------------------")
            await ctx.send(embeds=team2)
            msg2 = await ctx.send('Fetching live streams...')
            lives = gd.getTwitchLive(df_players.get('link'))
            if not lives:   
                await msg2.edit(content='No one is streaming in this lobby.')
            else:
                await msg2.edit(content="----------------------------------- LIVESTREAMS -----------------------------------")
                await ctx.send('\n'.join(lives))
        print('Live fetch for ' + str(arg) + ' complete.')

    @commands.command()
    async def users(self, ctx):
        lst = []
        for key in self.users.keys():
            lst.append(key)
        await ctx.send(lst)

    @commands.command()
    async def mates(self, ctx, arg):
        id = self.users.get(arg)
        if id == None:
            await ctx.send("User does not exist. Use \\users to see users.")
            return
        req = await gd.getMates(id)
        disc = gd.load_json('data/discordUsers.json')
        df = pd.DataFrame(req)
        df = df.drop(0)
        df = df[df['mate_id'].isin(disc.values())]
        df["names"] = ''
        for key, value in disc.items():
            df.loc[df['mate_id'] == value, "names"] = key
        df = df.drop(columns=['matches', 'mate_id'])
        df['win %'] = df['wins']/df['matches_played']
        df['win %'] = (df['win %'] * 100).map('{:.2f}%'.format)
        df_sort = df.sort_values(by='win %', ascending=False)
        await ctx.send(arg + ' winrate with mates:')
        await ctx.send(df_sort)

async def setup(bot):
    await bot.add_cog(Deadlock(bot))



  

