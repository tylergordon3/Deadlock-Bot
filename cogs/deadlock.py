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
import re

ranks, na_leaderboard, eu_leaderboard, hero = initialize.init()
guild_id = [546868043838390299]


class Deadlock(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.users = gd.load_json("data/users.json")
        self.dataListener.start()
        self.liveMessage = ""

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
        link = "https://tracklock.gg/players/"
        disc_users = self.users["discord"]
        today_ranks = {}
        for user in disc_users:
            print(f"Getting rank today for: {user}")
            user_link = link + str(disc_users[user])
            html = await gd.getHTML(user_link)
            name = html.find("h1", class_="font-bold text-2xl text-white").text

            for hero_lb in all_lb:
                lb_players = list(hero_lb.values())[0]
                for player in lb_players:
                    if player[0] == name:
                        hero = str(list(hero_lb.keys())[0])
                        # today_ranks is list of dicts -> each dict is username mapped to list of ranks
                        if player[0] not in today_ranks.keys():
                            today_ranks[player[0]] = {hero: player[1]}
                        else:
                            if player[1] not in list(today_ranks[player[0]].keys()):
                                today_ranks[player[0]][hero] = player[1]
                            else:
                                print(
                                    f"getRanksToday::Error {player[1]} already in {today_ranks[player[0]][hero]}"
                                )
        return today_ranks

    async def update(self, today_ranks):
        discDict = gd.load_json("data/hero_disc.json")
        today = rd.getCurrentDay()
        for player in discDict:
            name = await gd.getTracklockUser(player, self.users["discord"])
            try:
                player_rank_today = today_ranks[name]
            except:
                break
            player_dict = discDict[player]
            id = list(player_dict.keys())[0]
            currData = player_dict[id]
            for hero in player_rank_today:
                hero_data_dict = currData["hero"]
                if hero in hero_data_dict:
                    record = hero_data_dict[hero]
                    if today not in hero_data_dict[hero]:
                        record[today] = player_rank_today[hero]
                        print(
                            f"For {name}, {hero} rank {player_rank_today[hero]} updated in dict for {today}"
                        )
                    else:
                        print(
                            f"For {name}, {hero} rank {player_rank_today[hero]} already in dict for {today}"
                        )
                        if record[today] != player_rank_today[hero]:
                            record[today] = player_rank_today[hero]
                            print(
                                f"For {name}, {hero} rank {player_rank_today[hero]} being re updated for today"
                            )
                else:
                    print(
                        f"For {name}, {hero} rank {player_rank_today[hero]} not in json yet."
                    )
                    hero_data_dict[hero] = {f"{today}": player_rank_today[hero]}

        with open("data/hero_disc.json", mode="w", encoding="utf-8") as write_file:
            json.dump(discDict, write_file, indent=4)

    async def heroLeaderboards(self):
        # all_leaderboards -> List of lists containing hero leaderboard as tuples
        print(f"Getting hero leaderboards - all.")
        all_leaderboards = await Deadlock.loadHeroData(self)
        print(f"Getting today's hero ranks.")
        today_ranks = await Deadlock.getRanksToday(self, all_leaderboards)
        print(f"Updating today's hero rank data.")
        await Deadlock.update(self, today_ranks)

    @tasks.loop(hours=12)
    async def dataListener(self):
        await Deadlock.heroLeaderboards(self)
        # self.herolb = await Deadlock.heroLeaderboards(self)
        if rd.checkDataLastUpd(8):
            await rd.get_daily()
            # self.herolb = await Deadlock.heroLeaderboards(self)
            await Deadlock.heroLeaderboards(self)

    async def live_autocomp_all(
        self,
        interaction: discord.Interaction,
        curr: str,
    ) -> List[app_commands.Choice[str]]:
        choices = self.users["discord"] | self.users["all"]
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

    """
        Match Id
        Winning Team if decided
        Team 0 Net Worth
        Team 1 Net Worth
        Team 0 Obj Mask
        Team 1 Obj Mask
         cols=['team0NetWorth', 'team1NetWorth', 'spectators', 'team0Objectives', 'team1Objectives']
    """

    async def stop(self):
        Deadlock.liveStatus.stop()
        self.liveMessage = ""

    """
        TEAM 0 -> Yellow Amber Hand
        TEAM 1 -> Blue Sapphire Flame

        Lane 1 -> purple
        Lane 2 -> blue
        Lane 3 -> green
        Lane 4 -> yellow
    """

    def get_bool(mask):
        core = bool(mask & (1 << 0))
        tier1_lane1 = bool(mask & (1 << 1))
        tier1_lane2 = bool(mask & (1 << 2))
        tier1_lane3 = bool(mask & (1 << 3))
        tier1_lane4 = bool(mask & (1 << 4))
        tier2_lane1 = bool(mask & (1 << 5))
        tier2_lane2 = bool(mask & (1 << 6))
        tier2_lane3 = bool(mask & (1 << 7))
        tier2_lane4 = bool(mask & (1 << 8))
        titan = bool(mask & (1 << 9))
        titan_shield_generator_1 = bool(mask & (1 << 10))
        titan_shield_generator_2 = bool(mask & (1 << 11))
        barrack_boss_lane1 = bool(mask & (1 << 12))
        barrack_boss_lane2 = bool(mask & (1 << 13))
        barrack_boss_lane3 = bool(mask & (1 << 14))
        barrack_boss_lane4 = bool(mask & (1 << 15))
        g = tier1_lane1 + tier1_lane2 + tier1_lane3 + tier1_lane4
        w = tier2_lane1 + tier2_lane2 + tier2_lane3 + tier2_lane4
        baseg = (
            barrack_boss_lane1
            + barrack_boss_lane2
            + barrack_boss_lane3
            + barrack_boss_lane4
        )
        shrine = titan_shield_generator_1 + titan_shield_generator_2
        obj = f"Guardians: {g}/4 | Walkers: {w}/4 | Base Guards: {baseg}/4 | Shrines: {shrine}/2 | Titan Weak: {not titan}"
        return obj

    @tasks.loop(minutes=1)
    async def liveStatus(self, msg, id):
        liveData = gd.getLiveLoop(id)
        if liveData == "":
            print("LiveData returned empty, stopping loop.")
            await Deadlock.stop(self)
        else:
            print("\nRunning live loop.")
            start_time = liveData[5]
            match_duration = rd.timeSince(start_time)
            str = f"Amber Hand\nNet Worth: {liveData[0]:,d}\nObjectives: {Deadlock.get_bool(liveData[3])}\n\nSapphire Flame\nNet Worth: {liveData[1]:,d}\nObjectives: {Deadlock.get_bool(liveData[4])}\n\nDuration: {match_duration}\nSpectators: {liveData[2]}"
            print(str)
            await msg.edit(content=str)

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
        if choices in self.users["all"]:
            id = self.users["all"][choices]
            df_players = gd.getLive(self.users["all"][choices])
        elif choices in self.users["discord"]:
            id = self.users["discord"][choices]
            df_players = gd.getLive(self.users["discord"][choices])
        else:
            df_players = pd.DataFrame()

        if df_players.empty:
            err_msg = "Player not found, potential reasons: \n- Lobby elo too low\n- Player not in a game\n- Player is in active game but duration of game is less than 3 minutes\n Check /users for available users."
            await ctx.send(f"Error during execution:\n```py\n{err_msg}\n```")
        else:
            msg = await ctx.send("Fetching players in game.....")
            team1, team2 = await ud.getProfiles(
                df_players, ranks, na_leaderboard, eu_leaderboard, hero
            )
            await msg.edit(content="PLAYERS IN GAME:")
            await ctx.send(
                "----------------------------------- TEAM 1 -----------------------------------"
            )
            await ctx.send(embeds=team1)
            await ctx.send(
                "----------------------------------- TEAM 2 -----------------------------------"
            )
            await ctx.send(embeds=team2)
            msg2 = await ctx.send("Fetching live streams...")
            lives = gd.getTwitchLive(df_players.get("link"))
            if not lives:
                await msg2.edit(content="No one is streaming in this lobby.")
            else:
                await msg2.edit(
                    content="----------------------------------- LIVESTREAMS -----------------------------------"
                )
                await ctx.send("\n".join(lives))
        print("Live fetch for " + str(choices) + " complete.")
        msg = await ctx.send("Grabbing additional match data.")
        if not Deadlock.liveStatus.is_running():
            Deadlock.liveStatus.start(self, msg, id)

    @app_commands.command(description="Show users available for commands.")
    async def users(self, interaction: discord.Interaction):
        lst = []
        dlst = []
        for key in self.users["all"].keys():
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
        formatted = f"```\n{markdown}\n```"
        await interaction.response.send_message(formatted)

    @app_commands.command(description="Fetch hero leaderboards for user.")
    @app_commands.autocomplete(choices=live_autocomp_disc)
    async def heros(self, interaction: discord.Interaction, choices: str):
        discDict = gd.load_json("data/hero_disc.json")
        today = rd.getCurrentDay()
        name = await gd.getTracklockUser(choices, self.users["discord"])

        player = discDict[choices]
        id = list(player.keys())[0]
        heros = player[id]
        description = ""
        hero_lst = heros["hero"]
        for hero in hero_lst:
            thisHero = hero_lst[hero]
            if today in thisHero:
                description = description + f"{hero}: Rank {thisHero[today]}\n"

        if description == "":
            await interaction.response.send_message("No ranks")
        embed = discord.Embed(title=f"{name} Ranks", description=description)
        embed.set_footer(text=f"As of {today}")
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Deadlock(bot))
