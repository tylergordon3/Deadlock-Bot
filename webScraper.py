import requests
import discord
from bs4 import BeautifulSoup
import re
import pandas as pd

def getTwitchLive(links):
    streams = []
    for id in links:
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


def getImgUrl(rank_imgs, rank, subrank):
    row = rank_imgs.iloc[rank]['IMAGES']
    key = list(row.keys())[subrank-1]
    img_url = row[key]
    return img_url

def makeEmbedRanked(lb, ranks, hero, region, rank_imgs, acc_name, account):
    leaderboard = lb.iloc[0]['rank']
    rank = ranks[ranks['tier'] == lb.iloc[0]['ranked_rank']].iloc[0]['name']
    sub_rank = lb.iloc[0]['ranked_subrank']
    img_url = getImgUrl(rank_imgs, lb.iloc[0]['ranked_rank'], sub_rank)
    description = "\n"+region+": "+str(leaderboard)+"\n" + rank+" "+str(sub_rank)+"\nPlaying: "+hero
    embed = discord.Embed(url=account, title=acc_name, description=description)
    embed.set_thumbnail(url=img_url)
    return embed

def makeEmbedUnranked(hero, acc_name, account):
    embed = discord.Embed(url=account, title=acc_name, description="Ranked outside top 1,000\nPlaying: " + hero)
    return embed

    
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


def getProfiles(df_players, ranks, na_lb, eu_lb, hero_df):
    team1embeds = []
    team2embeds = []
    rank_imgs = getImages(ranks)

    for account in df_players['link']:
        response = requests.get(account)
        soup = BeautifulSoup(response.content, 'html.parser')
        acc_name = soup.find('h1', class_ ='font-bold text-2xl text-white').text 
        na_lb_check = na_lb[na_lb['account_name'] == acc_name]
        eu_lb_check = eu_lb[eu_lb['account_name'] == acc_name]

        acc_hero_id = df_players.loc[df_players['link'] == account]['hero_id'].values[0]

        hero = hero_df.loc[hero_df['id'] == acc_hero_id]['name'].values[0]

        if len(na_lb_check) == 1:
            lb = na_lb_check
            region = 'NA'
            print('Making NA Ranked Embed')
            embed = makeEmbedRanked(lb, ranks, hero, region, rank_imgs, acc_name, account)
        elif len(eu_lb_check) == 1:
            lb = eu_lb_check 
            region = 'EU'
            print('Making EU Ranked Embed')
            embed = makeEmbedRanked(lb, ranks, hero, region, rank_imgs, acc_name, account)
        else:
            region = ''
            print('Making Unranked Embed')
            embed = makeEmbedUnranked(hero, acc_name, account)

        team = df_players.loc[df_players['link'] == account]['team'].values[0]
        match team:
            case 0:
                team1embeds.append(embed)
            case 1: 
                team2embeds.append(embed)
    return team1embeds, team2embeds
   