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


def getProfiles(ids, ranks, na_lb, eu_lb, hero):
    account_lst = []
    rank_imgs = getImages(ranks)
    for id in ids:
        response = requests.get(id)
        soup = BeautifulSoup(response.content, 'html.parser')
        name = soup.find('h1', class_ ='font-bold text-2xl text-white').text
        na_lb_check = na_lb[na_lb['account_name'] == name]
        eu_lb_check = eu_lb[eu_lb['account_name'] == name]

        if len(na_lb_check) == 1:
            rank_num = na_lb_check.iloc[0]['rank']
            rank =  na_lb_check.iloc[0]['ranked_rank']
            rank_name = ranks[ranks['tier'] == rank].iloc[0]['name']
            subrank = na_lb_check.iloc[0]['ranked_subrank']
            description = "NA Leaderboard Rank: " + str(rank_num) + "\n" + rank_name + " " + str(subrank)
            row = rank_imgs.iloc[rank]['IMAGES']
            key = list(row.keys())[subrank-1]
            img_url = row[key]
            embed = discord.Embed(url=id, title=name, description=description)
            embed.set_image(url=img_url)
            account_lst.append(embed)
        elif len(eu_lb_check) == 1:
            print(eu_lb_check)
            rank_num = eu_lb_check.iloc[0]['rank']
            print(rank_num)
            rank =  eu_lb_check.iloc[0]['ranked_rank']
            rank_name = ranks[ranks['tier'] == rank].iloc[0]['name']
            subrank = eu_lb_check.iloc[0]['ranked_subrank']
            description = "EU Leaderboard Rank: " + str(rank_num) + "\n" + rank_name + " " + str(subrank)
            print(description)
            row = rank_imgs.iloc[rank]['IMAGES']
            key = list(row.keys())[subrank-1]
            img_url = row[key]
            embed = discord.Embed(url=id, title=name, description=description)
            embed.set_image(url=img_url)
            account_lst.append(embed)
        else: 
            description = ""
            embed = discord.Embed(url=id, title=name,description=description)
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