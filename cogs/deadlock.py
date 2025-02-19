import asyncio
import discord
from discord import app_commands
from discord.ext import commands, tasks
from typing import List

import tools.initialize as initialize
import pandas as pd
import tools.getData as gd
import tools.useData as ud
import tools.reqData as rd
import os
import re

ranks, na_leaderboard, eu_leaderboard, hero = initialize.init()
guild_id = [546868043838390299]

class Deadlock(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.users = gd.load_json("data/users.json")
        self.dataListener.start()
        self.herolb = []

    async def loadHeroData(self):
        path = 'dataDaily/hero_lb/'
        files = [f for f in os.listdir(path)]
        all = []
        for f in files:
            data = gd.load_json(path + f)
            hero = f[:-5]
            pull = [(d['account_name'], d['rank']) for d in data['entries']]
            all.append({hero:pull})
        return all
    
    async def getRanksToday(self, all_lb):
        link = 'https://tracklock.gg/players/'
        disc_users = self.users['discord']
        today_ranks = {}
        for user in disc_users:
            user_link = link + str(disc_users[user])
            html = await gd.getHTML(user_link)
            name = html.find('h1', class_ ='font-bold text-2xl text-white').text
            for hero_lb in all_lb:
                lb_players = list(hero_lb.values())[0]
                for player in lb_players:
                    if player[0] == name:
                        hero = str(list(hero_lb.keys())[0])
                        # today_ranks is list of dicts -> each dict is username mapped to list of ranks
                        if player[0] not in today_ranks.keys():
                            today_ranks[player[0]] = { hero : player[1]}
                        else:
                            if player[1] not in list(today_ranks[player[0]].keys()):
                                today_ranks[player[0]][hero] = player[1]
                            else:
                                print(f"getRanksToday::Error {player[1]} already in {today_ranks[player[0]][hero]}")
        return today_ranks              
    
    async def update(self, today_ranks):
        discDict = gd.load_json('data/hero_disc.json')
        today = rd.getCurrentDay()
        needUpdate = []
        for player in discDict:
            # print current_dict[player] --> {'311616544': [{'Lady Geist': {'2/17/2025': 35}}, {'Abrams': {'2/17/2025': 45}}]}
            name = await gd.getTracklockUser(player, self.users['discord'])
            try:
                player_rank_today = today_ranks[name]
            except:
                break
                
            player_dict = discDict[player]
            id = list(player_dict.keys())[0]
            charactersNeedUpdate = []
        
            checker = [k for d in player_dict[id] for k in d.keys()]
            print(f"Checker: {checker}")


            for char_dict in player_dict[id]:
                # print(char_dict) --> {'Lady Geist': {'2/17/2025': 35}} , {'Abrams': {'2/17/2025': 45}}
                name = list(char_dict.keys())[0]
                records = char_dict[name]
                # print(records) --> {'2/15/2025': 35, '2/16/2025': 41}
                dates_entered = list(records.keys())
                # print(dates_entered) --> ['2/15/2025', '2/16/2025']
                if today in dates_entered:
                    print("Today already entered for " + name)
                else:
                    print("Entering today for " + name)
                    charactersNeedUpdate.append(name)
            needUpdate.append({id:charactersNeedUpdate})
        print(needUpdate)
        return needUpdate
       
    async def heroLeaderboards(self):
        # all_leaderboards -> List of lists containing hero leaderboard as tuples
        all_leaderboards = await Deadlock.loadHeroData(self)
        today_ranks = await Deadlock.getRanksToday(self, all_leaderboards)
        await Deadlock.update(self, today_ranks)
   
    @tasks.loop(hours=12)
    async def dataListener(self):
        self.herolb = await Deadlock.loadHeroData(self)
        if (rd.checkDataLastUpd(8)):
            await rd.get_daily()
            self.herolb = await Deadlock.loadHeroData(self)

    async def live_autocomp_all(self, 
        interaction: discord.Interaction, curr: str, 
        ) -> List[app_commands.Choice[str]]:
        choices = self.users['discord'] | self.users['all']
        return [
            app_commands.Choice(name=choice, value=choice)
            for choice in choices if curr.lower() in choice.lower()
        ]

    async def live_autocomp_disc(self, 
        interaction: discord.Interaction, curr: str, 
        ) -> List[app_commands.Choice[str]]:
        choices = self.users['discord'] 
        return [
            app_commands.Choice(name=choice, value=choice)
            for choice in choices if curr.lower() in choice.lower()
        ]
    
    @app_commands.command(description="Fetch a user's live match displaying ranks of both teams.")
    @app_commands.autocomplete(choices=live_autocomp_all)
    async def live(self, interaction: discord.Interaction, choices: str, delay_minutes: int) :    
        if (delay_minutes > 10 | delay_minutes < 0) :
            delay_minutes = 0
        ctx = interaction.channel
        print("Sleeping for " + str(delay_minutes*60) + " seconds.")
        await interaction.response.send_message("Waiting " + str(delay_minutes*60) + " seconds before fetching live match info for: " + choices)
        await asyncio.sleep(delay_minutes*60)
        print("Back from sleep.")
        if choices in self.users['all']:
            df_players = gd.getLive(self.users['all'][choices])
        elif choices in self.users['discord']:
            df_players = gd.getLive(self.users['discord'][choices])
        else:
            df_players = pd.DataFrame()
       
        if df_players.empty:
            err_msg = 'Player not found, potential reasons: \n- Lobby elo too low\n- Player not in a game\n- Player is in active game but duration of game is less than 3 minutes\n Check /users for available users.'
            await ctx.send( f"Error during execution:\n```py\n{err_msg}\n```")
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
        print('Live fetch for ' + str(choices) + ' complete.')

    @app_commands.command(description="Show users available for commands.")
    async def users(self, interaction: discord.Interaction):
        lst = []
        dlst = []
        for key in self.users['all'].keys():
            lst.append(key)
        for key in self.users['discord'].keys():
            dlst.append(key)
        await interaction.response.send_message("## Users availble for ONLY /live \n" + '\n'.join(lst) + "\n## Users availble for /live & /mates \n" + '\n'.join(dlst))
      
    @app_commands.command(description="Display a player's win rates when playing with other discord members.")
    @app_commands.autocomplete(choices=live_autocomp_disc)
    async def mates(self, interaction: discord.Interaction, choices: str):
        id = self.users['discord'].get(choices)
        if id == None:
            await interaction.response.send_message("User does not exist. Use /users to see users.")
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
        df_sort = df.sort_values(by='win %', ascending=False)
        df_sort['win %'] = (df_sort['win %'] * 100).map('{:.2f}%'.format)
    
        df_sort['loss'] = df_sort['matches_played']-df_sort['wins']
        base = "{wins}-{loss}"
        df_sort['W-L'] = [base.format(wins=x, loss=y)
            for x,y in zip(df_sort['wins'], df_sort['loss'])]
        
        df_sort = df_sort.drop(columns=['wins', 'matches_played', 'loss'])
        markdown = df_sort.to_markdown(index=False)
        formatted = f"```\n{markdown}\n```"
        await interaction.response.send_message(formatted)
        
    '''
    @app_commands.command(description="Fetch hero leaderboards for user.")
    @app_commands.autocomplete(choices=live_autocomp_disc)
    async def heros(self, interaction: discord.Interaction, choices: str):
        for embed in self.herolb:
            print(str(self.users['discord'][choices]))
            print(str(embed.footer))
            if (str(self.users['discord'][choices]) in str(embed.footer)):
                    await interaction.response.send_message(embed=embed)
                    return
        await interaction.response.send_message("Not found!")'''
                

async def setup(bot):
    await bot.add_cog(Deadlock(bot))



  

