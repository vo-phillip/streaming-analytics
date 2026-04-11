import redis, json, numpy as np, time
from collections import deque
from config import REDIS_HOST, REDIS_PORT, RIOT_API_KEY, RIOT_REGION

WINDOW_LEN = 100
ALPHA = 0.05

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

points_window = deque(maxlen=WINDOW_LEN)
ema = None
while True:
    data = r.lpop("champions")
    if data is None:
        time.sleep(5)
        continue
    champion = json.loads(data)
    points_window.append(champion["championPoints"])
    if len(points_window) >= 2:
        mean = np.mean(points_window)
        sd = np.std(points_window)
        if sd == 0:
            continue
        if ema is None:
            ema = mean
        else:
            ema = ALPHA * champion["championPoints"] + (1 - ALPHA) * ema
        
        z_score = (champion["championPoints"] - mean) / float(sd)
        
        print(f"Champion {champion['championId']} | Points: {champion['championPoints']} | Z-Score: {z_score:.2f} | EMA: {ema:.0f}")
