import requests
import json
import matplotlib.pyplot as plt
import numpy as np

site = "https://analytics.deadlock-api.com/v2/leaderboard/Row"

hist = "https://data.deadlock-api.com/v2/players/108601750/match-history"
# hist = "https://data.deadlock-api.com/v2/players/336921993/match-history"

gfreek = 108601750
durk = 336921993


with open("hero.json") as f:
    d = json.load(f)
    print(d)

response = requests.get(site)
resp = requests.get(hist)

# print(response)
# print(resp.json())

dict = resp.json()
dmatch = dict["matches"]

res = []
worth = []

for i, val in enumerate(dmatch):
    res.append(val["match_result"])
    worth.append(val["net_worth"])


res = np.array(res)
worth = np.array(worth)

wins = worth[res == 0]
loss = worth[res == 1]

# plt.boxplot([wins, loss], labels=["W", "L"])
# plt.ylabel("Souls")
# plt.title("durk Souls vs W/L")
# plt.show()
# print(dict["matches"][0]["denies"])


mmr = "https://analytics.deadlock-api.com/v2/players/108601750/mmr-history"

r = requests.get(mmr).json()

active = "https://data.deadlock-api.com/v1/active-matches?account_id=" + str(gfreek)

live = requests.get(active)

data = live.json()

players = []

print(type(data[0]["players"]))

site = "https://tracklock.gg/players/"

for player in data[0]["players"]:
    players.append(site + str(player["account_id"]))


if not live.json():
    print("Player is not in an active game retard!")
else:
    print("ok")
