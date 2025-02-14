import requests
import pandas as pd
import json
import os
import getData as gd

path = "../data"

def get_daily():
    files = [f for f in os.listdir("dataDaily") if f.endswith(".json")]
    for f in files:
        path = 'dataDaily/' + f
        region = f[:-5]
        data = requests.get(f'https://data.deadlock-api.com/v1/leaderboard/{region}')
        with open(path, mode='w', encoding="utf-8") as write_file:
            json.dump(data.json(),write_file, indent=4)
     



def get_periodic():
    ranks = requests.get('https://assets.deadlock-api.com/v2/ranks').json()
    hero =  pd.DataFrame(requests.get('https://assets.deadlock-api.com/v2/heroes?only_active=true').json())
    
    df_hero = hero[['id','name']]

    with open("../data/hero_ids.json", mode="w", encoding="utf-8") as write_file:
        res=df_hero.to_json(orient='records', index=False)
        parse=json.loads(res)
        json.dump(parse, write_file, indent=4)
    
    with open("../data/ranks.json", mode="w", encoding="utf-8") as write_file:
        json.dump(ranks, write_file, indent=4)
    
get_daily()