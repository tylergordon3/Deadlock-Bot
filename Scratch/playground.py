import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

link = 'https://data.deadlock-api.com/v1/leaderboard/NAmerica'
ranks = 'https://assets.deadlock-api.com/v2/ranks'
lb_raw = requests.get(link).json()
lb = lb_raw['entries']

rank = requests.get(ranks).json()
rank_df = pd.DataFrame(rank)
#print(rank_df)


df = pd.DataFrame(lb)


name = 'Mawty Maw'

res = df[df['account_name'] == name]

#print(res)
#print(res.iloc[0]['ranked_rank'])
r = res.iloc[0]['ranked_rank']
print(rank_df)


rank_df['img2'] = rank_df['images'].copy()
#print(rank_df['img2'])
ri = rank_df['img2']
big = []
r = re.compile('^small_subrank(1[0-1]|[0-9])$')
#print(rank_df[rank_df['tier'] == r].iloc[0]['name'])
# print(rank_df['images'])
#nlist = list(filter(r.match))
big.append({'small':ri[0]['small']})
ri = ri.drop(0)
for row in ri:
    res = {key: val for key, val in row.items() if re.search(r, key)}
    big.append(res)
rank_df['img2'] = big
#rank_df['img2'] = big
#print(rank_df)
print(rank_df)
#print('\n')
#print(big)

print(rank_df.iloc[11]['img2'])

dict = rank_df.iloc[11]['img2']
k = list(dict.keys())[1]
url = dict[k]
print(url)

hero_link = 'https://assets.deadlock-api.com/v2/heroes?only_active=true'
hlink = requests.get(hero_link).json()
dfh = pd.DataFrame(hlink)
dfh_clean = [dfh['id'],dfh['name']]

