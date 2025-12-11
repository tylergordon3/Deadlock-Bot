import asyncio
import discord
from discord import app_commands
from discord.ext import commands, tasks
from typing import List
import json

import tools.initialize as initialize
import pandas as pd
import tools.getData as gd
import tools.useData as ud
import tools.reqData as rd
import os
import datetime as dt

guild_id = [os.environ.get("GUILD_ID")]


class Deadlock(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.users = gd.load_json("data/users.json")
        self.dataListener.start()
        self._tasks = []
        self.path = "/mnt/share"

    async def loadHeroData(self):
        path = "dataDaily/hero_lb/"
        files = [f for f in os.listdir(path)]
        all = []
        for f in files:
            data = gd.load_json(path + f)
            hero = f[:-5]
            pull = [(d["account_name"], d["rank"]) for d in data["entries"]]
            all.append({hero: pull})
        return all

    async def getRanksToday(self, all_lb):
        dict = gd.load_json("data/user_dict.json")
        disc_users = dict["discord"]
        today_ranks = {}
        for userID in disc_users.keys():
            name = disc_users[userID]
            print(f"Getting rank today for: {name}")
            for hero_lb in all_lb:
                lb_players = list(hero_lb.values())[0]
                for player in lb_players:
                    if player[0] == name:
                        hero = str(list(hero_lb.keys())[0])
                        # today_ranks is list of dicts -> each dict is username mapped to list of ranks
                        if userID not in today_ranks.keys():
                            today_ranks[userID] = {hero: player[1]}
                        else:
                            if hero not in list(today_ranks[userID].keys()):
                                today_ranks[userID][hero] = player[1]
                            else:
                                print(
                                    f"getRanksToday::Error {hero} already in {list(today_ranks[userID].keys())}"
                                )
        print(f'RETURNING TODAY RANKS: {today_ranks}')
        return today_ranks

    async def update(self, today_ranks):
        '''
        Docstring for update
        
        :param self: self
        :param today_ranks: Dict mapping SteamID to another dict with hero ranks for today
        '''
        discDict = gd.load_json("data/hero_disc.json")
        today = rd.getCurrentDay()
        time = dt.datetime.now()
        time = dt.datetime.strftime(time, "%Y-%m-%d %H:%M:%S")
        discDict["upd"] = time
        for userID in discDict:
            if userID != "upd":
                name = await gd.getTracklockUserByID(userID)
                try:
                    player_rank_today = today_ranks[userID]
                except:
                    print(f"No Leaderboard: Name: {name}, Player: {userID}")
                    continue

                player_dict = discDict[userID]
                
                # currData - list of ranks and dates for hero
                currData = player_dict['hero']
            
                # player_rank_today - Dict with hero : rank from today
                # For each hero ranked today
                for hero in player_rank_today:
                    # If hero is in dict of previous data
                    if hero in currData.keys():
                        # Get previous data
                        record = currData[hero]

                        # Check if today has already been grabbed
                        if today not in currData[hero]:
                            record[today] = player_rank_today[hero]
                            print(
                                f"For {name}, {hero} rank {player_rank_today[hero]} dict entry added, {today}"
                            )
                        else:
                            if record[today] != player_rank_today[hero]:
                                record[today] = player_rank_today[hero]
                                print(
                                    f"For {name}, {hero} rank {record[today]} has been updated to: {player_rank_today[hero]}"
                                )
                    else:
                        print(
                            f"For {name}, {hero} rank {player_rank_today[hero]} not in json yet."
                        )
                        currData[hero] = {f"{today}": player_rank_today[hero]}

        with open("data/hero_disc.json", mode="w", encoding="utf-8") as write_file:
            json.dump(discDict, write_file, indent=4)

    async def heroLeaderboards(self):
        # all_leaderboards -> List of lists containing hero leaderboard as tuples
        print(f"Loading hero leaderboards - all.")
        all_leaderboards = await Deadlock.loadHeroData(self)
        print(f"Loading today's hero ranks.")
        today_ranks = await Deadlock.getRanksToday(self, all_leaderboards)
        print(f"Updating today's hero rank data.")
        await Deadlock.update(self, today_ranks)

    @tasks.loop(hours=1)
    async def dataListener(self):
        #await Deadlock.internal_refresh(self)
        #await rd.get_daily()
        #await Deadlock.heroLeaderboards(self)
        if rd.checkDataLastUpd(4):
            await Deadlock.internal_refresh(self)
            await rd.get_daily()
            await Deadlock.heroLeaderboards(self)

    async def live_autocomp_all(
        self,
        interaction: discord.Interaction,
        curr: str,
    ) -> List[app_commands.Choice[str]]:
        choices = self.users["discord"] | self.users["others"]
        return [
            app_commands.Choice(name=choice, value=choice)
            for choice in choices
            if curr.lower() in choice.lower()
        ]

    async def live_autocomp_disc(
        self,
        interaction: discord.Interaction,
        curr: str,
    ) -> List[app_commands.Choice[str]]:
        choices = self.users["discord"]
        return [
            app_commands.Choice(name=choice, value=choice)
            for choice in choices
            if curr.lower() in choice.lower()
        ]

    async def stop(self):
        Deadlock.liveStatus.stop()

    """
        TEAM 0 -> Yellow Amber Hand
        TEAM 1 -> Blue Sapphire Flame

        Lane 1 -> purple
        Lane 2 -> blue
        Lane 3 -> green
        Lane 4 -> yellow
    """

    def formatObjective(val, team):
        match team:
            case "AH":
                match val:
                    case 0:
                        return ":white_small_square:"
                    case 1:
                        return ":small_orange_diamond:"
            case "SF":
                match val:
                    case 0:
                        return ":white_small_square:"
                    case 1:
                        return ":small_blue_diamond:"

    def get_bool(ah_mask, sf_mask, team):
        ah_tier1_lane1 = Deadlock.formatObjective(bool(ah_mask & (1 << 1)), "AH")
        ah_tier1_lane3 = Deadlock.formatObjective(bool(ah_mask & (1 << 3)), "AH")
        ah_tier1_lane4 = Deadlock.formatObjective(bool(ah_mask & (1 << 4)), "AH")
        ah_tier2_lane1 = Deadlock.formatObjective(bool(ah_mask & (1 << 5)), "AH")
        ah_tier2_lane3 = Deadlock.formatObjective(bool(ah_mask & (1 << 7)), "AH")
        ah_tier2_lane4 = Deadlock.formatObjective(bool(ah_mask & (1 << 8)), "AH")
        if not bool(ah_mask & (1 << 9)):
            ah_titan = ":red_circle:"
        else:
            ah_titan = Deadlock.formatObjective(bool(ah_mask & (1 << 9)), "AH")
        ah_shield1 = Deadlock.formatObjective(bool(ah_mask & (1 << 10)), "AH")
        ah_shield2 = Deadlock.formatObjective(bool(ah_mask & (1 << 11)), "AH")
        ah_barrack_boss_lane1 = Deadlock.formatObjective(
            bool(ah_mask & (1 << 12)), "AH"
        )
        ah_barrack_boss_lane3 = Deadlock.formatObjective(
            bool(ah_mask & (1 << 14)), "AH"
        )
        ah_barrack_boss_lane4 = Deadlock.formatObjective(
            bool(ah_mask & (1 << 15)), "AH"
        )

        sf_tier1_lane1 = Deadlock.formatObjective(bool(sf_mask & (1 << 1)), "SF")
        sf_tier1_lane3 = Deadlock.formatObjective(bool(sf_mask & (1 << 3)), "SF")
        sf_tier1_lane4 = Deadlock.formatObjective(bool(sf_mask & (1 << 4)), "SF")
        sf_tier2_lane1 = Deadlock.formatObjective(bool(sf_mask & (1 << 5)), "SF")
        sf_tier2_lane3 = Deadlock.formatObjective(bool(sf_mask & (1 << 7)), "SF")
        sf_tier2_lane4 = Deadlock.formatObjective(bool(sf_mask & (1 << 8)), "SF")

        if not bool(sf_mask & (1 << 9)):
            sf_titan = ":red_circle:"
        else:
            sf_titan = Deadlock.formatObjective(bool(sf_mask & (1 << 9)), "SF")
        sf_shield1 = Deadlock.formatObjective(bool(sf_mask & (1 << 10)), "SF")
        sf_shield2 = Deadlock.formatObjective(bool(sf_mask & (1 << 11)), "SF")
        sf_barrack_boss_lane1 = Deadlock.formatObjective(
            bool(sf_mask & (1 << 12)), "SF"
        )
        sf_barrack_boss_lane3 = Deadlock.formatObjective(
            bool(sf_mask & (1 << 14)), "SF"
        )
        sf_barrack_boss_lane4 = Deadlock.formatObjective(
            bool(sf_mask & (1 << 15)), "SF"
        )

        str_ah = (
            f"\u3000\u2007\u2007{sf_titan}\n"
            f"\u3000{sf_shield1}\u3000{sf_shield2}\n"
            f"{sf_barrack_boss_lane1}\u3000{sf_barrack_boss_lane3}\u3000{sf_barrack_boss_lane4}\n"
            f"{sf_tier2_lane1}\u3000{sf_tier2_lane3}\u3000{sf_tier2_lane4}\n"
            f"{sf_tier1_lane1}\u3000{sf_tier1_lane3}\u3000{sf_tier1_lane4}\n"
            f"\n"
            f"{ah_tier1_lane4}\u3000{ah_tier1_lane3}\u3000{ah_tier1_lane1}\n"
            f"{ah_tier2_lane4}\u3000{ah_tier2_lane3}\u3000{ah_tier2_lane1}\n"
            f"{ah_barrack_boss_lane4}\u3000{ah_barrack_boss_lane3}\u3000{ah_barrack_boss_lane1}\n"
            f"\u3000{ah_shield2}\u3000{ah_shield1}\n"
            f"\u3000\u2007\u2007{ah_titan}"
        )

        str_sf = (
            f"\u3000\u2007\u2007{ah_titan}\n"
            f"\u3000{ah_shield1}\u3000{ah_shield2}\n"
            f"{ah_barrack_boss_lane1}\u3000{ah_barrack_boss_lane3}\u3000{ah_barrack_boss_lane4}\n"
            f"{ah_tier2_lane1}\u3000{ah_tier2_lane3}\u3000{ah_tier2_lane4}\n"
            f"{ah_tier1_lane1}\u3000{ah_tier1_lane3}\u3000{ah_tier1_lane4}\n"
            f"\n"
            f"{sf_tier1_lane4}\u3000{sf_tier1_lane3}\u3000{sf_tier1_lane1}\n"
            f"{sf_tier2_lane4}\u3000{sf_tier2_lane3}\u3000{sf_tier2_lane1}\n"
            f"{sf_barrack_boss_lane4}\u3000{sf_barrack_boss_lane3}\u3000{sf_barrack_boss_lane1}\n"
            f"\u3000{sf_shield2}\u3000{sf_shield1}\n"
            f"\u3000\u2007\u2007{sf_titan}"
        )

        if team == 1:
            return str_sf
        return str_ah

    """0 'team0NetWorth'
    1 'team1NetWorth' 
    2'spectators' 
    3 'team0Objectives'  
    4 'team1Objectives']"""

    @tasks.loop(minutes=1)
    async def liveStatus(self, msg, id, team):
        liveData = gd.getLiveLoop(id)
        if liveData == "":
            print("LiveData returned empty, stopping loop.")
            await msg.edit(content="Game has concluded.")
            await Deadlock.stop(self)
        else:
            start_time = liveData[5]
            match_duration = rd.timeSince(start_time)
            print(f"Running live loop at match duration: {match_duration}")
            if team == 1:
                enemy = "Amber Hand"
                usr_team = "Sapphire Flame"
            else:
                usr_team = "Amber Hand"
                enemy = "Sapphire Flame"
            str = (
                f"\nSpectators: {liveData[2]}\n\n{enemy}\nNet Worth: {liveData[1]:,d}\n"
                + Deadlock.get_bool(liveData[3], liveData[4], team)
                + f"\n{usr_team}\nNet Worth: {liveData[0]:,d}"
            )

            embed = discord.Embed(
                title=f"Match Duration: {match_duration}", description=str
            )
            await msg.edit(content="", embed=embed)

    @app_commands.command(
        description="Fetch a user's live match displaying ranks of both teams."
    )
    @app_commands.autocomplete(choices=live_autocomp_all)
    async def live(
        self, interaction: discord.Interaction, choices: str, delay_minutes: int
    ):
        if delay_minutes > 10 | delay_minutes < 0:
            delay_minutes = 0
        ctx = interaction.channel
        print("Sleeping for " + str(delay_minutes * 60) + " seconds.")
        await interaction.response.send_message(
            "Waiting "
            + str(delay_minutes * 60)
            + " seconds before fetching live match info for: "
            + choices
        )
        await asyncio.sleep(delay_minutes * 60)
        print("Back from sleep.")
        if choices in self.users["others"]:
            id = self.users["others"][choices]
            df_players = gd.getLive(self.users["others"][choices])
        elif choices in self.users["discord"]:
            id = self.users["discord"][choices]
            df_players = gd.getLive(self.users["discord"][choices])
        else:
            print('Fetching for: ', choices)
            id = choices
            df_players = gd.getLive(choices)

        if df_players.empty:
            err_msg = "Player not found, potential reasons: \n- Match is not in top 200 active matches\n- Player not in a game\n- Player is in active game but duration of game is less than 3 minutes\n Check /users for available users."
            await ctx.send(f"Error during execution:\n```py\n{err_msg}\n```")
        else:

            choice_team = df_players.loc[
                df_players["link"] == f"https://tracklock.gg/players/{id}", "team"
            ].values[0]

            msg = await ctx.send("Fetching players in game.....")
            ranks, na_leaderboard, eu_leaderboard, hero = initialize.init()
            team1, team2 = await ud.getProfiles(
                df_players, ranks, na_leaderboard, eu_leaderboard, hero
            )
            await msg.edit(content="PLAYERS IN GAME:")
            await ctx.send(embeds=team1)
            await ctx.send(embeds=team2)
            msg2 = await ctx.send("Fetching live streams...")
            lives = await gd.getTwitchLive(df_players.get("link"))
            if not lives:
                await msg2.edit(content="No one is streaming in this lobby.")
            else:
                to_send = "\n".join(lives)
                await msg2.edit(content=to_send)
            print("Live fetch for " + str(choices) + " complete.")
            msg = await ctx.send("Grabbing additional match data.")
            if not Deadlock.liveStatus.is_running():
                Deadlock.liveStatus.start(self, msg, id, choice_team)
            else:
                await msg.edit(
                    content="Match data being fetched for another match already."
                )

    @app_commands.command(description="Show users available for commands.")
    async def users(self, interaction: discord.Interaction):
        lst = []
        dlst = []
        for key in self.users["others"].keys():
            lst.append(key)
        for key in self.users["discord"].keys():
            dlst.append(key)
        await interaction.response.send_message(
            "## Users availble for ONLY /live \n"
            + "\n".join(lst)
            + "\n## Users availble for /live & /mates \n"
            + "\n".join(dlst)
        )

    @app_commands.command(
        description="Display a player's win rates when playing with other discord members."
    )
    @app_commands.autocomplete(choices=live_autocomp_disc)
    async def mates(self, interaction: discord.Interaction, choices: str):
        id = self.users["discord"].get(choices)
        if id == None:
            await interaction.response.send_message(
                "User does not exist. Use /users to see users."
            )
            return
        req = await gd.getMates(id)
        df = pd.DataFrame(req)
        df = df.drop(0)
        df = df[df["mate_id"].isin(self.users["discord"].values())]
        df["names"] = ""
        for key, value in self.users["discord"].items():
            df.loc[df["mate_id"] == value, "names"] = key
        df = df.drop(columns=["matches", "mate_id"])
        df["win %"] = df["wins"] / df["matches_played"]
        df_sort = df.sort_values(by="win %", ascending=False)
        df_sort["win %"] = (df_sort["win %"] * 100).map("{:.2f}%".format)

        df_sort["loss"] = df_sort["matches_played"] - df_sort["wins"]
        base = "{wins}-{loss}"
        df_sort["W-L"] = [
            base.format(wins=x, loss=y)
            for x, y in zip(df_sort["wins"], df_sort["loss"])
        ]
        df_sort = df_sort.drop(columns=["wins", "matches_played", "loss"])
        markdown = df_sort.to_markdown(index=False)
        formatted = f"Teammate Stats for: {choices}\n```\n{markdown}\n```"
        await interaction.response.send_message(formatted)

    @app_commands.command(description="Fetch all hero ranks")
    async def ranks (self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        today = rd.getCurrentDay()
        hero_disc = gd.load_json("data/hero_disc.json")
        output = ''
        tuples = []
        for key in hero_disc:
            try:
                _ = int(key)
            except:
                continue
            name = await gd.getTracklockUserByID(int(key))
            userHeroDict = hero_disc[key]
            userHeroDict = userHeroDict['hero']
           
            for hero in userHeroDict.keys():
                hero_ranks = userHeroDict[hero]
                if today in hero_ranks.keys():
                    hero_tpl = (name, hero, hero_ranks[today])
                    tuples.append(hero_tpl)
        sorted_tup = sorted(tuples, key=lambda item: (item[0], item[2]))
        used_names = []
        for tup in sorted_tup:
            if tup[0] not in used_names:
                output += f'\n__{tup[0]}__\n'
                used_names.append(tup[0])
            output += f'{tup[1]}: #{tup[2]}\n'
        embed = discord.Embed(title=f"Hero Ranks for {today}", description=output)
        await interaction.followup.send(embed=embed)

    @app_commands.command(description="Fetch hero leaderboards for user.")
    @app_commands.autocomplete(choices=live_autocomp_disc)
    async def heros(self, interaction: discord.Interaction, choices: str):
        hero_disc = gd.load_json("data/hero_disc.json")
        today = rd.getCurrentDay()
        try:
            userID = self.users['discord'][choices]
            name = await gd.getTracklockUserByID(userID)
            heros = hero_disc[str(userID)]
            description = ""
            hero_lst = heros["hero"]
            
            for hero in hero_lst:
                thisHero = hero_lst[hero]
                if today in thisHero:
                    description = description + f"{hero}: Rank {thisHero[today]}\n"
            if description == "":
                await interaction.response.send_message("No ranks")
            else:
                embed = discord.Embed(title=f'{name} Ranks', description=description)
                embed.set_footer(text=f"As of {today}")
                await interaction.response.send_message(embed=embed)  
        except:
            await interaction.response.send_message(
                "No ranks - error with info entered."
            )

    @app_commands.command(description="Update Steam Usernames for saved accounts.")
    async def refresh(self, interaction: discord.Interaction):
        path = 'data/user_dict.json'
        data = gd.load_json(path)
        await interaction.response.defer(thinking=True)
        for category in data:
            keys = list(data[category].keys())
            results = []
            for key in keys:
                results.append(await gd.getNameFromSteamID(key))
            for key, value in zip(keys, results):
                data[category][key] = value
        with open(path, mode="w", encoding="utf-8") as write_file:
            json.dump(data, write_file, indent=4)

        reversed = {
            section: {v: int(k) for k,v in entries.items()}
            for section, entries in data.items()
        }
        path_OG = 'data/users.json'
        with open(path_OG, mode="w", encoding="utf-8") as write_file:
            json.dump(reversed, write_file, indent=4)
        self.users = gd.load_json("data/users.json")
        await interaction.followup.send("Refresh complete!")

    async def internal_refresh(self):
        print('Starting internal refresh.')
        path = 'data/user_dict.json'
        data = gd.load_json(path)
        for category in data:
            keys = list(data[category].keys())
            results = []
            for key in keys:
                results.append(await gd.getNameFromSteamID(key))
            for key, value in zip(keys, results):
                data[category][key] = value
        async def write_json(path, data):
            await asyncio.to_thread(
            lambda: json.dump(
                data,
                open(path, "w", encoding="utf-8"),
                ensure_ascii=False
            )
        )
        await write_json(path, data)
        reversed = {
            section: {v: int(k) for k,v in entries.items()}
            for section, entries in data.items()
        }
        path_OG = 'data/users.json'
        await write_json(path_OG, reversed)
        self.users = gd.load_json("data/users.json")
        print("Internal refresh complete!")

async def setup(bot):
    await bot.add_cog(Deadlock(bot))
