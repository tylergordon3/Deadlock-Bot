import requests
import pandas as pd
import tools.getData as gd

def init():
    na = gd.load_json("dataDaily/NAmerica.json")
    df_na = pd.DataFrame(na['entries'])

    eu = gd.load_json("dataDaily/Europe.json")
    df_eu = pd.DataFrame(eu['entries'])

    rank = gd.load_json("data/ranks.json")
    df_rank = pd.DataFrame(rank)

    hero = pd.DataFrame(gd.load_json("data/hero_ids.json"))
    df_hero = hero[['id','name']]

    return df_rank, df_na, df_eu, df_hero