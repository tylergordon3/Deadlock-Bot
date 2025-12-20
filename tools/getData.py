import requests
import pandas as pd
from bs4 import BeautifulSoup
import json
import aiohttp
import asyncio
import random
import tools.getDataAdv as gda


async def getTracklockUser(user, disc_users):
    link = "https://tracklock.gg/players/"
    user_link = link + str(disc_users[user])
    html = await gda.getHTML(user_link)
    if html is None:
        print(f"NoneType for: {user_link}")
    try:
        name = html.find("h1", class_="text-white font-montserrat text-[36px] font-semibold leading-normal").text
    except:
        print(f"ERROR::getTracklockUser  Finding name for {user_link}") 
        return 'NAME_ERROR' 
    return name

async def getTracklockUserByID(userID):
    link = "https://tracklock.gg/players/"
    user_link = link + str(userID)
    html = await gda.getHTML(user_link)
    try:
        name = html.find("h1", class_="text-white font-montserrat text-[36px] font-semibold leading-normal").text
    except:
        print(f"ERROR::getTracklockUser  Finding name for {user_link}") 
        return 'NAME_ERROR' 
    return name

async def getNameFromSteamID(id):
    link = "https://steamid.xyz/"
    user_link = link + str(id)
    html = await getHTML(user_link)
    name = html.find("h1", class_="h3 value").text
    return name

def read_txt(filename):
    with open(filename, "r") as file:
        text = file.read()
        return text


def write_txt(filename, new):
    with open(filename, "w") as file:
        file.write(new)


def load_json(filename):
    """Fetch default config file"""
    try:
        with open(filename, encoding="utf8") as data:
            return json.load(data)
    except FileNotFoundError:
        raise FileNotFoundError("JSON file wasn't found")


def dump_json(filename, data):
    try:
        with open(filename, "wb") as file:
            json.dump(data, file)
    except FileNotFoundError:
        raise FileNotFoundError("JSON file wasn't found")


async def getHTML(link, retries=5, base_delay=1.0):
    for attempt in range(retries):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(link) as r:
                    # 429 or 5xx → retry
                    if r.status in (429, 500, 502, 503, 504):
                        if attempt < retries - 1:
                            delay = base_delay * (2 ** attempt) + random.uniform(0, 0.2)
                            await asyncio.sleep(delay)
                            continue

                    if r.status == 200:
                        content = await r.text()
                        return BeautifulSoup(content, "html.parser")

                    # Non-retriable failure
                    r.raise_for_status()
            except (aiohttp.ClientError, asyncio.TimeoutError):
                if attempt < retries - 1:
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 0.2)
                    await asyncio.sleep(delay)
                    continue
            raise
    return None  # if all retries fail

async def getWebData(link, retries=20, base_delay=1.0):
    for attempt in range(retries):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(link) as r:
                    # 429 or 5xx → retry
                    if r.status in (429, 500, 502, 503, 504):
                        if attempt < retries - 1:
                            delay = base_delay * (2 ** attempt) + random.uniform(0, 0.2)
                            await asyncio.sleep(delay)
                            continue

                    if r.status == 200:
                        content = await r.json()
                        return content

                    # Non-retriable failure
                    r.raise_for_status()
            except (aiohttp.ClientError, asyncio.TimeoutError):
                if attempt < retries - 1:
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 0.2)
                    await asyncio.sleep(delay)
                    continue
            raise
    return None  # if all retries fail

async def getMates(id):
    link = f"https://api.deadlock-api.com/v1/players/{id}/mate-stats"
    async with aiohttp.ClientSession() as session:
        async with session.get(link) as r:
            if r.status == 200:
                return await r.json()


def getLiveLoop(id):
    active = "https://api.deadlock-api.com/v1/matches/active?account_id=" + str(id)
    live = requests.get(active)

    if not live.json():
        empty = ""
        return empty
    data = live.json()
    colsData = [
        data[0]["net_worth_team_0"],
        data[0]["net_worth_team_1"],
        data[0]["spectators"],
        data[0]["objectives_mask_team0"],
        data[0]["objectives_mask_team1"],
        data[0]["start_time"],
    ]
    return colsData


def getLive(id):
    active = "https://api.deadlock-api.com/v1/matches/active?account_id=" + str(id)
    live = requests.get(active)
    data = live.json()
    players = []
    site = "https://tracklock.gg/players/"
    if not live.json():
        empty = pd.DataFrame()
        return empty
    else:
        for player in data[0]["players"]:
            tracklock = site + str(player["account_id"])
            team = player["team"]
            hero = player["hero_id"]
            players.append([tracklock, team, hero])

    df_players = pd.DataFrame(players)

    df_players.columns = ["link", "team", "hero_id"]
    return df_players


async def getTwitchLive(links):
    streams = []
    async with aiohttp.ClientSession() as session:
        for url in links:
            async with session.get(url) as resp:
                html = await resp.text()
            soup = BeautifulSoup(html, "html.parser")

            twitch = ""
            for a in soup.find_all("a"):
                href = a.get("href")
                if href and "twitch" in href:
                    twitch = href

            if twitch:
                # fetch twitch page
                async with session.get(twitch) as resp:
                    twitch_html = await resp.text()

                # detect if live
                if "isLiveBroadcast" in twitch_html:
                    streams.append(twitch)
        print("Returning twitch streams")
    return streams


def getHeroLeaderboard(region, hero_id, acc_name):
    match region:
        case "NA":
            link = "https://api.deadlock-api.com/v1/leaderboard/NAmerica/" + str(
                hero_id
            )
        case "EU":
            link = "https://api.deadlock-api.com/v1/leaderboard/Europe/" + str(hero_id)

    response = requests.get(link).json()
    df_hero = pd.DataFrame(response["entries"])
    lb_check = df_hero[df_hero["account_name"] == acc_name]

    if len(lb_check) == 1:
        rank = lb_check.iloc[0]["rank"]
        return rank
    return -1
