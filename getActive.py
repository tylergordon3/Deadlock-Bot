import requests
import json
import numpy as np
import pandas as pd
'''
def getLive(id):
    active = "https://data.deadlock-api.com/v1/active-matches?account_id=" + str(id)
    live = requests.get(active)
    data = live.json()
    players = []
    site = 'https://tracklock.gg/players/'

    if not live.json():
        return players
    else:
        for player in data[0]['players']:
            players.append(site + str(player['account_id']))
        return players
'''
    
def getLive(id):
    active = "https://data.deadlock-api.com/v1/active-matches?account_id=" + str(id)
    live = requests.get(active)
    data = live.json()
    players = []
    site = 'https://tracklock.gg/players/'
    
    if not live.json():
        empty = pd.DataFrame()
        return empty
    else:
        for player in data[0]['players']:
            tracklock = site + str(player['account_id']);
            team =  player['team']
            hero = player['hero_id']
            players.append([tracklock,team,hero])

    df_players = pd.DataFrame(players)
    df_players.columns= ['link', 'team', 'hero_id']
    return df_players