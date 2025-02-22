import requests
import pandas as pd
from bs4 import BeautifulSoup
import json
import aiohttp


async def getTracklockUser(user, disc_users):
    link = 'https://tracklock.gg/players/'
    user_link = link + str(disc_users[user])
    html = await getHTML(user_link)
    name = html.find('h1', class_ ='font-bold text-2xl text-white').text
    return name

def read_txt(filename):
    with open (filename, 'r') as file:
        text = file.read()
        return text

def write_txt(filename, new):
    with open (filename, 'w') as file:
        file.write(new)
        
    
def load_json(filename):
    """ Fetch default config file """
    try:
        with open(filename, encoding='utf8') as data:
            return json.load(data)
    except FileNotFoundError:
        raise FileNotFoundError("JSON file wasn't found")
    
def dump_json(filename, data):
    try:
        with open(filename, 'wb') as file:
            json.dump(data, file)
    except FileNotFoundError:
        raise FileNotFoundError("JSON file wasn't found")
    

async def getHTML(link):
    async with aiohttp.ClientSession() as session:
        async with session.get(link) as r:
            if r.status == 200:
                content = await r.text()
                soup = BeautifulSoup(content, 'html.parser')
                return soup

async def getMates(id): 
    link = f'https://analytics.deadlock-api.com/v2/players/{id}/mate-stats'
    async with aiohttp.ClientSession() as session:
        async with session.get(link) as r:
            if r.status == 200:
                return await r.json()

def getLiveLoop(id):
        active = "https://data.deadlock-api.com/v1/active-matches?account_id=" + str(id)
        live = requests.get(active)
        
        if not live.json():
            empty = ""
            return empty
        data = live.json()
        colsData = [data[0]['net_worth_team_0'],
            data[0]['net_worth_team_1'],
            data[0]['spectators'],
            data[0]["objectives_mask_team0"],
            data[0]["objectives_mask_team1"],
            data[0]["start_time"]]
       
        
        return colsData

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
    print('Returning twitch streams')
    return streams

def getHeroLeaderboard(region, hero_id, acc_name):
    match region:
        case "NA":
            link = 'https://data.deadlock-api.com/v1/leaderboard/NAmerica/'+str(hero_id)
        case "EU":
            link = 'https://data.deadlock-api.com/v1/leaderboard/Europe/'+str(hero_id) 
    
    response = requests.get(link).json()
    df_hero = pd.DataFrame(response['entries'])
    lb_check = df_hero[df_hero['account_name'] == acc_name]

    if len(lb_check) == 1:
        rank = lb_check.iloc[0]['rank']
        return rank
    return -1
    
    