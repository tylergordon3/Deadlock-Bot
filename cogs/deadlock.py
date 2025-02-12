import asyncio
from discord.ext import commands
import discord

import tools.initialize as initialize
import pandas as pd

import tools.getData as gd
import tools.useData as ud

ranks, na_leaderboard, eu_leaderboard, hero = initialize.init()

class Deadlock(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.users = gd.load_json("data/users.json")
        self.bad = gd.read_txt("data/bad.txt")

    @commands.command()
    async def live(self, ctx, arg1, arg2=0):    
        print("Sleeping for " + str(arg2*60))
        await asyncio.sleep(arg2*60)
        print("Back from sleep.")
        if arg1 in self.users['all']:
            df_players = gd.getLive(self.users['all'][arg1])
        elif arg1 in self.users['discord']:
            df_players = gd.getLive(self.users['discord'][arg1])
        else:
            df_players == 0
       
        if df_players.empty:
            await ctx.send('Player not found. Check /users for available users.')
        else:
           
            msg = await ctx.send('Fetching players in game.....')
            team1, team2= await ud.getProfiles(df_players, ranks, na_leaderboard, eu_leaderboard, hero)
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
        print('Live fetch for ' + str(arg1) + ' complete.')

    
    @commands.command()
    async def users(self, ctx):
        lst = []
        dlst = []
        for key in self.users['all'].keys():
            lst.append(key)
        for key in self.users['discord'].keys():
            dlst.append(key)
        await ctx.send("## Users availble for ONLY /live")
        await ctx.send('\n'.join(lst))
        await ctx.send("## Users availble for /live & /mates")
        await ctx.send('\n'.join(dlst))

    @commands.command()
    async def mates(self, ctx, arg):
        id = self.users['discord'].get(arg)
        if id == None:
            await ctx.send("User does not exist. Use /users to see users.")
            return
        req = await gd.getMates(id)
        df = pd.DataFrame(req)
        df = df.drop(0)
        df = df[df['mate_id'].isin(self.users['discord'].values())]
        df["names"] = ''
        for key, value in self.users['discord'].items():
            df.loc[df['mate_id'] == value, "names"] = key
        df = df.drop(columns=['matches', 'mate_id'])
        df['win %'] = df['wins']/df['matches_played']
        df['win %'] = (df['win %'] * 100).map('{:.2f}%'.format)
        
        df_sort = df.sort_values(by='win %', ascending=False)

        df_sort['loss'] = df_sort['matches_played']-df_sort['wins']
        base = "{wins}-{loss}"
        df_sort['W-L'] = [base.format(wins=x, loss=y)
            for x,y in zip(df_sort['wins'], df_sort['loss'])]
        
        df_sort = df_sort.drop(columns=['wins', 'matches_played', 'loss'])
        markdown = df_sort.to_markdown(index=False)
        formatted = f"```\n{markdown}\n```"
        await ctx.send(formatted)

    @commands.command()
    async def addShitters(self, ctx, arg):
        self.bad = self.bad + "\n" + arg
        gd.write_txt("data/bad.txt", self.bad)
        await ctx.send("Added: " +  arg)


    @commands.command()
    async def shitters(self, ctx):
        await ctx.send("".join(self.bad))


async def setup(bot):
    await bot.add_cog(Deadlock(bot))



  

