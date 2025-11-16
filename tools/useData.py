import discord
import tools.getData as gd
import re


def getImgUrl(rank_imgs, rank, subrank):
    row = rank_imgs.iloc[rank]["IMAGES"]
    key = list(row.keys())[subrank - 1]
    img_url = row[key]
    return img_url


def getImages(ranks):
    ranks["IMAGES"] = ranks["images"].copy()
    manip = ranks["IMAGES"]
    filtered = []
    r = re.compile("^small_subrank(1[0-1]|[0-9])$")
    filtered.append({"small": manip[0]["small"]})
    manip = manip.drop(0)

    for row in manip:
        result = {key: val for key, val in row.items() if re.search(r, key)}
        filtered.append(result)
    ranks["IMAGES"] = filtered
    return ranks


def makeEmbedRanked(
    lb, ranks, hero, region, rank_imgs, acc_name, account, hero_rank, team
):
    if team == "AH":
        color = 15844367
    else:
        color = 3447003
    leaderboard = lb.iloc[0]["rank"]
    badge = lb["badge_level"].values[0]
    ranked_rank = str(badge)[:-1]
    subrank = str(badge)[-1]
    rank = ranks[ranks["tier"] == int(ranked_rank)].iloc[0]["name"]

    img_url = getImgUrl(rank_imgs, int(ranked_rank), int(subrank))
    description = (
        "\n"
        + region
        + " Rank: "
        + str(leaderboard)
        + "\n"
        + rank
        + " "
        + str(subrank)
        + "\nPlaying: "
        + hero
    )
    if hero_rank > 0:
        description += ", Rank: " + str(hero_rank)
    embed = discord.Embed(
        url=account, title=acc_name, description=description, color=color
    )
    embed.set_thumbnail(url=img_url)
    return embed


def makeEmbedUnranked(hero, acc_name, account, hero_rank, team):
    if team == "AH":
        color = 15844367
    else:
        color = 3447003
    description = "Playing: " + hero
    if hero_rank > 0:
        description += ", Rank: " + str(hero_rank)
    embed = discord.Embed(
        url=account, title=acc_name, description=description, color=color
    )
    return embed


async def getProfiles(df_players, ranks, na_lb, eu_lb, hero_df):

    team1embeds = []
    team2embeds = []
    rank_imgs = getImages(ranks)
    print("Fetching Profiles")
    for account in df_players["link"]:
        team = df_players.loc[df_players["link"] == account]["team"].values[0]
        if team == 0:
            color = "AH"
        else:
            color = "SF"
        html = await gd.getHTML(account)
        acc_name = html.find("h1", class_="font-bold text-2xl text-white").text
        na_lb_check = na_lb[na_lb["account_name"] == acc_name]
        eu_lb_check = eu_lb[eu_lb["account_name"] == acc_name]

        acc_hero_id = df_players.loc[df_players["link"] == account]["hero_id"].values[0]

        hero = hero_df.loc[hero_df["id"] == acc_hero_id]["name"].values[0]

        if len(na_lb_check) == 1:
            lb = na_lb_check
            region = "NA"
            hero_rank = gd.getHeroLeaderboard(region, acc_hero_id, acc_name)
            embed = makeEmbedRanked(
                lb, ranks, hero, region, rank_imgs, acc_name, account, hero_rank, color
            )
        elif len(eu_lb_check) == 1:
            lb = eu_lb_check
            region = "EU"
            hero_rank = gd.getHeroLeaderboard(region, acc_hero_id, acc_name)
            embed = makeEmbedRanked(
                lb, ranks, hero, region, rank_imgs, acc_name, account, hero_rank, color
            )
        else:
            hero_rank_na = gd.getHeroLeaderboard("NA", acc_hero_id, acc_name)
            hero_rank_eu = gd.getHeroLeaderboard("EU", acc_hero_id, acc_name)
            if hero_rank_na > 0:
                embed = makeEmbedUnranked(hero, acc_name, account, hero_rank_na, color)
            elif hero_rank_eu > 0:
                embed = makeEmbedUnranked(hero, acc_name, account, hero_rank_eu, color)
            else:
                embed = makeEmbedUnranked(hero, acc_name, account, -1, color)

        match team:
            case 0:
                team1embeds.append(embed)
            case 1:
                team2embeds.append(embed)

    print("Embeds being returned")
    return team1embeds, team2embeds
