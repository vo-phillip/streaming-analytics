from config import REDIS_HOST, REDIS_PORT, RIOT_API_KEY, RIOT_REGION
import requests
import redis
import json
import time

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def get_platinum_players():
    url = f"https://{RIOT_REGION}.api.riotgames.com/lol/league/v4/entries/RANKED_SOLO_5x5/PLATINUM/I?page=1"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return [player["puuid"] for player in data[:50]]
    else:
        print(f"Error fetching data from Riot API: {response.status_code}")
        return []

def get_champion_mastery(puuid):
    url = f"https://{RIOT_REGION}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        champions = response.json()
        return [{"puuid": puuid, "championId": champ["championId"], "championLevel": champ["championLevel"], 
                 "championPoints": champ["championPoints"], "lastPlayTime": champ["lastPlayTime"]} for champ in champions[:10]]
    else:
        print(f"Error fetching champion mastery for {puuid}: {response.status_code}")
        return []

while True:
    platinum_players = get_platinum_players()
    for puuid in platinum_players:
        champion_data = get_champion_mastery(puuid)
        for champ in champion_data:
            entry_key = f"{puuid}:{champ['championId']}"
            if r.sismember("seen_entries", entry_key):
                continue
            r.rpush("champions", json.dumps(champ))
            r.sadd("seen_entries", entry_key)
        # Sleep to avoid hitting rate limits
        time.sleep(1)  
    # Sleep for 2 minutes before fetching again
    time.sleep(120)  

