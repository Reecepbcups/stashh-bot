import httpx, time, os, json

from dotenv import load_dotenv
from utils.notifications import discord_notification

# load env variables
load_dotenv()

# Default endpoints
API = "https://stashh.io/nfts/get"
API_COLLECTION_DATA = "https://stashh.io/collection/fetch"

# Load global needs from env / the .env file
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK", "")
CONTRACT = os.getenv("CONTRACT", "secret1dvd46mkjr8s4cl2czv03h9y82heeefc0hzlrat")
LISTING_LINK = os.getenv("LISTING_LINK", "https://stashh.io/asset/racn/RACOON%20{ID}")

# query headers
headers = {    
    "User-Agent": os.getenv("USER_AGENT", ""),
    "accept": "application/jsopyhonn, text/plain, */*",
    "accept-enconding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.5",
    "scheme": "https",
    "authorization": os.getenv("BEARER_TOKEN", ""),
    "content-type": "application/json",
    "origin": "https://stashh.io",
    "request-id": os.getenv("REQUESTS_ID", ""),
    "sec-ch-ua": '.Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
    "sec-ch-ua-mobile": "?1",
    "sec-ch-ua-platform": "Android",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "request-context": os.getenv("REQUESTS_CONTEXT", ""),
    "sec-fetch-site": "same-origin",
    "traceparent": os.getenv("TRACEPARENT", ""),
    "cookie": os.getenv("COOKIE", ""),
} 

# recently sold nfts
recently_sold = {
    "params":  {
        "limit":50,
        "skip":0,
        "collections":[CONTRACT],
        "is_badge":False,"sort_by":"sold_date","ascending":False,"is_spam":False,"query_id":"Y6FkHqytBfuH9eqaAaRD"
    }
}

nft_stats = {
    "address": os.getenv("ADDRESS", "racn")
}

filename = "past_sold.json"
past_sold = {}
def load_nft_times_from_file() -> dict:
    global past_sold
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            json.dump({}, f)
    with open(filename, 'r') as f:
        past_sold = json.load(f)       
    return past_sold
def _save_nfts() -> None:
    if len(past_sold) > 0:
        with open(filename, 'w') as f:
            json.dump(past_sold, f)
def update_nft_sell_date(nft_id: str, new_sold_time: int, scrt_amt: float, dollar_amt: float):
    global past_sold
    past_sold[nft_id] = {
        "timestamp": new_sold_time, # epoch in seconds
        "scrt_amt": scrt_amt,
        "dollar_amt": dollar_amt
    }
    _save_nfts()


def epoch_to_human(epoch_seconds):
    # 2022-09-01 14:18:05    
    tz = time.tzname[time.daylight]
    return time.strftime('%Y-%m-%d %Hh %Mm', time.localtime(epoch_seconds)) + f" {tz}"

def get_nft_stats():
    response = httpx.post(API_COLLECTION_DATA, json=nft_stats, headers=headers)
    data = response.json()  #; print(data.keys())

    avg_dollar = f"${round(data['avg_dollar'], 2)}"
    total_volume = data['collection']['total_volume']

    # print(f"avg_dollar: {avg_dollar= f"${round(data['avg_dollar'], 2)}" trades = } max: {max} min: {min} trades: {trades} daily_trades: {daily_trades} daily_volume: {daily_volume} total_volume: {round(total_volume, 0):,} USDC")
    return {
        "avg_dollar": avg_dollar,
        "max": data['max'],
        "floor": data['min'],
        "trades": data['trades'],
        "daily_trades": data['daily_trades'],
        "daily_volume": data['daily_volume'],
        "total_volume": total_volume
    }

def get_latest_sales():
    # make a post requests to API with params
    response = httpx.post(API, json=recently_sold, headers=headers)
    data = response.json()['nfts']

    stats = get_nft_stats()

    # Loop through NFTs return values, revered so that it goes oldest to newest.
    for nft in reversed(data):
        name = nft['name']
        _id = nft['id']
        num_likes = len(nft['likes'])
        rank = nft['rank']
        coll_name = nft['coll_name']
        listing_link = LISTING_LINK.replace("{ID}", nft['id'].split(" ")[1])

        # lat sold
        scrt_price = nft['last_sold']['price']
        dollar_price = nft['last_sold']['dollar_price']
        timestamp = int(int(nft['last_sold']['timestamp'])/1_000)
        # human_timestamp = epoch_to_human(timestamp)
        url = nft['thumbnail'][0]['url']
        # print(f"COLLECTION: {coll_name} -> {name} Rank #{rank} likes:{num_likes} scrt:{scrt_price} ${dollar_price}. Image: {url}")

        # check if the _id is in the past_sold dict, if so, check that the timestamp is newer. If it is not, continue to next check
        if _id in past_sold:
            if timestamp <= past_sold[_id]["timestamp"]:
                continue
            
        # if is first run, run this here then comment out. Set limit for most recent sold to 500
        # update_nft_sell_date(_id, timestamp, scrt_price, dollar_price); continue        
        

        lastScrtAmt = float(past_sold[_id]['scrt_amt'])
        lastDollarAmt = float(past_sold[_id]['dollar_amt'])

        scrt_difference = round(float(scrt_price) - lastScrtAmt, 2)
        dollar_difference = round(float(dollar_price) - lastDollarAmt, 2)

        scrt_percent = round((scrt_difference / lastScrtAmt) * 100, 2)
        dollar_percent = round((dollar_difference / lastDollarAmt) * 100, 2)

        sign = "+" if scrt_difference > 0 else "" # auto does negative        

        discord_notification(
            webook_url=WEBHOOK_URL,
            title=f"PURCHASE:\n{name} Rank #{rank}", 
            description=f"", 
            color=os.getenv("COLOR", "ffffff").replace("#", ""), 
            values={
                "LINK": [listing_link, True],
                "SCRT": [f"{scrt_price}\t(${dollar_price})", False],
                "Change Since Last Sale": [f"{sign}{scrt_difference}SCRT ({sign}{scrt_percent}%)\n{sign}${dollar_difference} ({sign}{dollar_percent}%)", False],
                "LIKES": [f"+{num_likes}", False],
                "FLOOR / AVG $": [f"Floor: ${stats['floor']}\nAverage: {stats['avg_dollar']}", False],
                "TIME SOLD": [f"<t:{int(timestamp)}>\n(<t:{int(timestamp)}:R>)", False],
            }, 
            thumbnail=os.getenv("THUMBNAIL_IMAGE", ""), 
            image=url, 
            footerText=""
        )
        update_nft_sell_date(_id, timestamp, scrt_price, dollar_price)
        time.sleep(1.3) # discord rate limit


if __name__ == "__main__":
    load_nft_times_from_file() # load past sold NFTs
    get_latest_sales()