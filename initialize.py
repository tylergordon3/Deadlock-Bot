import requests
import pandas as pd

def init():
    lb_link = 'https://data.deadlock-api.com/v1/leaderboard/NAmerica'
    ranks_link = 'https://assets.deadlock-api.com/v2/ranks'
    hero_link ='https://assets.deadlock-api.com/v2/heroes?only_active=true'

    lb_raw = requests.get(lb_link).json()
    ranks = requests.get(ranks_link).json()
    hero = pd.DataFrame(requests.get(hero_link).json())

    df_lb = pd.DataFrame(lb_raw['entries'])
    df_rank = pd.DataFrame(ranks)
    df_hero = hero[['id','name']]

    return df_rank, df_lb, df_hero