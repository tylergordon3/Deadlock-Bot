import requests
import pandas as pd

def init():
    na_lb_link = 'https://data.deadlock-api.com/v1/leaderboard/NAmerica'
    eu_lb_link = 'https://data.deadlock-api.com/v1/leaderboard/Europe'
    ranks_link = 'https://assets.deadlock-api.com/v2/ranks'
    hero_link ='https://assets.deadlock-api.com/v2/heroes?only_active=true'

    na_lb_raw = requests.get(na_lb_link).json()
    eu_lb_raw = requests.get(eu_lb_link).json()
    ranks = requests.get(ranks_link).json()
    hero = pd.DataFrame(requests.get(hero_link).json())

    df_na_lb = pd.DataFrame(na_lb_raw['entries'])
    df_eu_lb = pd.DataFrame(eu_lb_raw['entries'])
    df_rank = pd.DataFrame(ranks)
    df_hero = hero[['id','name']]

    return df_rank, df_na_lb, df_eu_lb, df_hero