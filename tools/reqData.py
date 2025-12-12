import requests
import pandas as pd
import json
import os
import tools.getData as gd
import datetime as dt


def timeSince(start):
    match_start = dt.datetime.fromtimestamp(start)
    curr_time = dt.datetime.now()
    duration = curr_time - match_start
    durStr = str(duration).split(".")[0]
    return durStr


def checkLastTime():
    last = os.stat("dataDaily/NAmerica.json").st_mtime
    last_datetime = dt.datetime.fromtimestamp(last)
    return last_datetime


def getCurrentDay():
    curr_datetime = dt.datetime.now()

    year = curr_datetime.year
    month = curr_datetime.month
    day = curr_datetime.day

    today_str = str(month) + "/" + str(day) + "/" + str(year)
    return today_str


def checkLastUpd(json):
    try:
        update = dt.datetime.strptime(json["upd"], "%Y-%m-%d %H:%M:%S")
    except:
        print("checkLastUpd :: error getting last update time.")
        return
    now_dt = dt.datetime.now()

    now = dt.datetime.strftime(now_dt, "%Y-%m-%d %H:%M:%S")
    diff = now - update

    return


def checkDataLastUpd(threshold_hrs=12):
    nadict = gd.load_json("dataDaily/NAmerica.json")

    update = dt.datetime.strptime(nadict["upd"], "%Y-%m-%d %H:%M:%S")

    curr_datetime = dt.datetime.now()
    print(f"Current time: {curr_datetime}")
    print(f"Last Update Time: {update}")
    # last_datetime = checkLastTime()
    diff = curr_datetime - update

    threshold_min = threshold_hrs * 60

    bool = (diff.total_seconds() / 60) > threshold_min
    str = f"Last data update: {diff.total_seconds()/3600:.2f} hours ago."
    bool_str = " Updating data." if bool else " Not updating data."
    print(str + bool_str)
    return bool


async def get_daily():
    files = [f for f in os.listdir("dataDaily") if f.endswith(".json")]
    today = dt.datetime.now()
    today = dt.datetime.strftime(today, "%Y-%m-%d %H:%M:%S")

    #  "2025-02-28 21:55:06.540840"
    print("Getting daily NA & EU leaderboards.")
    for f in files:
        path = "dataDaily/" + f
        region = f[:-5]
        data_json = await gd.getWebData(f"https://api.deadlock-api.com/v1/leaderboard/{region}")
        data_json["upd"] = today
        with open(path, mode="w", encoding="utf-8") as write_file:
            json.dump(data_json, write_file, indent=4)

    print("Getting daily hero leaderboards.")
    hero_ids = gd.load_json("data/hero_ids.json")
    for hero in hero_ids:
        id = str(hero["id"])
        name = hero["name"]
        path = "dataDaily/hero_lb/" + name + ".json"
        data = requests.get(
            f"https://api.deadlock-api.com/v1/leaderboard/NAmerica/{id}"
        )
        data_json = data.json()
        data_json["upd"] = today
        with open(path, mode="w", encoding="utf-8") as write_file:
            json.dump(data_json, write_file, indent=4)
    print("Daily update completed.")


async def get_periodic():
    ranks = requests.get("https://assets.deadlock-api.com/v2/ranks").json()
    hero = pd.DataFrame(
        requests.get(
            "https://assets.deadlock-api.com/v2/heroes?only_active=true"
        ).json()
    )

    df_hero = hero[["id", "name"]]
    print("Getting static hero data.")

    with open("data/hero_ids.json", mode="w", encoding="utf-8") as write_file:
        res = df_hero.to_json(orient="records", index=False)
        parse = json.loads(res)
        json.dump(parse, write_file, indent=4)

    print("Getting static rank data.")
    with open("data/ranks.json", mode="w", encoding="utf-8") as write_file:
        json.dump(ranks, write_file, indent=4)
