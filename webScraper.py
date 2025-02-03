import requests
import discord
from bs4 import BeautifulSoup
import re
import pandas as pd

def getTwitchLive(ids):
    streams = []
    for id in ids:
        response = requests.get(id)
        soup = BeautifulSoup(response.content, 'html.parser')

        twitch = ''
        links = soup.find_all("a")
        for link in links:
            if 'twitch' in link.get("href"):
                twitch = link.get("href")

        if twitch != '':
            contents= requests.get(twitch).content.decode('utf-8')
            if 'isLiveBroadcast' in contents:
                streams.append(twitch)
    return streams


def getProfiles(ids, ranks, leaderboard, hero):
    account_lst = []
    rank_imgs = getImages(ranks)
    print(rank_imgs)
    for id in ids:
        response = requests.get(id)
        soup = BeautifulSoup(response.content, 'html.parser')
        name = soup.find('h1', class_ ='font-bold text-2xl text-white').text
        lb_check = leaderboard[leaderboard['account_name'] == name]
        if len(lb_check) != 1:
            description = ""
            embed = discord.Embed(url=id, title=name, description=description)
            account_lst.append(embed)
        else: 
            rank_num = lb_check.iloc[0]['rank']
            rank =  lb_check.iloc[0]['ranked_rank']
            rank_name = ranks[ranks['tier'] == rank].iloc[0]['name']
            subrank = lb_check.iloc[0]['ranked_subrank']
            description = "NA Leaderboard Rank: " + str(rank_num) + "\n" + rank_name + " " + str(subrank)
            
            row = rank_imgs.iloc[rank]['IMAGES']
            key = list(row.keys())[subrank-1]
            img_url = row[key]

            embed = discord.Embed(url=id, title=name, description=description)
            embed.set_image(url=img_url)
            account_lst.append(embed)

    return account_lst

def getImages(ranks):
    ranks['IMAGES'] = ranks['images'].copy()
    manip = ranks['IMAGES']
    filtered = []
    r = re.compile('^small_subrank(1[0-1]|[0-9])$')
    filtered.append({'small':manip[0]['small']})
    manip = manip.drop(0)
    
    for row in manip:
        result = {key: val for key, val in row.items() if re.search(r, key)}
        filtered.append(result)
    ranks['IMAGES'] = filtered
    return ranks