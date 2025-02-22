import requests
import json
import numpy as np
import pandas as pd
import discord


def getLive(id):
    active = "https://data.deadlock-api.com/v1/active-matches?account_id=" + str(id)
    live = requests.get(active)
    data = live.json()
    players = []
    site = "https://tracklock.gg/players/"

    if not live.json():
        return players
    else:
        for player in data[0]["players"]:
            tracklock = site + str(player["account_id"])
            team = player["team"]
            hero = player["hero_id"]
            players.append([tracklock, team, hero])

    # print(players)
    df_players = pd.DataFrame(players)
    df_players.columns = ["link", "team", "hero_id"]
    print(df_players)
    # print(df_players['link'])

    for id in df_players["link"]:
        print(df_players.loc[df_players["link"] == id]["team"].values[0])


users = {
    "Dregley": 1165359771,
    "Jack": 436326420,
    "Gord": 311616544,
    "Durk": 336921993,
    "Gfreek": 108601750,
    "Fraud": 1845301134,
    "BigSqueep": 1843363705,
    "CardboardBox": 190690317,
    "eido": 1676299122,
    "crayon": 84379844,
    "duck": 7100261,
    "deathy": 87624911,
    "mikaels": 385814004,
    "nkd": 34262576,
    "jonas": 74963221,
    "pkmk": 179489990,
    "eu?guy": 901357991,
    "pct": 84801726,
    "thirkl": 105263588,
    "bogus": 139190043,
}

getLive(1165359771)
