import requests
import json
import matplotlib.pyplot as plt
import numpy as np

users = {"Dregley" : 1165359771, "Jack" : 436326420, "Gord" : 311616544, "Durk" : 336921993,
         "Gfreek" : 1854653965, "Fraud" : 1845301134, "BigSqueep" : 1843363705, "CardboardBox" : 190690317}


def fetchLive(id):
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
    
