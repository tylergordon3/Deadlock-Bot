import requests
import pandas as pd
import json
import os
import tools.getData as gd
import datetime as dt


def checkLastTime():
    last = os.stat('dataDaily/NAmerica.json').st_mtime
    last_datetime = dt.datetime.fromtimestamp(last)
    return last_datetime

    
def checkDataLastUpd(threshold_hrs = 12):
    
    curr_datetime = dt.datetime.now()
    print(f'Current time: {curr_datetime}')
    last_datetime = checkLastTime()
    diff = curr_datetime - last_datetime

    threshold_min = threshold_hrs * 60

    bool = (diff.total_seconds()/60) > threshold_min
    str = f"Last data update: {diff.total_seconds()/3600:.2f} hours ago."
    bool_str = " Updating data." if bool else " Not updating data."
    print(str + bool_str)
    return bool

def get_daily():
    files = [f for f in os.listdir("dataDaily") if f.endswith(".json")]
    print('Getting daily NA & EU leaderboards.')
    for f in files:
        path = 'dataDaily/' + f
        region = f[:-5]
        data = requests.get(f'https://data.deadlock-api.com/v1/leaderboard/{region}')
        with open(path, mode='w', encoding="utf-8") as write_file:
            json.dump(data.json(),write_file, indent=4)

    print('Getting daily hero leaderboards.')
    hero_ids = gd.load_json('data/hero_ids.json')
    for hero in hero_ids:
        id = str(hero['id'])
        name = hero['name']

        path = 'dataDaily/hero_lb/' + name + '.json'
        data = requests.get(f'https://data.deadlock-api.com/v1/leaderboard/NAmerica/{id}')
        with open(path, mode='w', encoding="utf-8") as write_file:
            json.dump(data.json(), write_file, indent=4)



def get_periodic():
    ranks = requests.get('https://assets.deadlock-api.com/v2/ranks').json()
    hero =  pd.DataFrame(requests.get('https://assets.deadlock-api.com/v2/heroes?only_active=true').json())
    
    df_hero = hero[['id','name']]
    print('Getting static hero data.')
    with open("data/hero_ids.json", mode="w", encoding="utf-8") as write_file:
        res=df_hero.to_json(orient='records', index=False)
        parse=json.loads(res)
        json.dump(parse, write_file, indent=4)
    
    print('Getting static rank data.')
    with open("data/ranks.json", mode="w", encoding="utf-8") as write_file:
        json.dump(ranks, write_file, indent=4)
    
