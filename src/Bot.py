import httpx, string, random, time, os
from dotenv import load_dotenv
from utils.notifications import discord_notification

load_dotenv()

API = "https://stashh.io/nfts/get"
API_COLLECTION_DATA = "https://stashh.io/collection/fetch"

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK", "")
CONTRACT = os.getenv("CONTRACT", "secret1dvd46mkjr8s4cl2czv03h9y82heeefc0hzlrat")
LISTING_LINK = os.getenv("LISTING_LINK", "https://stashh.io/asset/racn/RACOON%20{ID}")


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
        "limit":24,"skip":0,
        "collections":[CONTRACT],
        "is_badge":False,"sort_by":"sold_date","ascending":False,"is_spam":False,"query_id":"Y6FkHqytBfuH9eqaAaRD"
    }
}
nft_stats = {
    "address": os.getenv("ADDRESS", "racn")
}

# TODO: floor price & stuffs
def epoch_to_human(epoch_seconds):
    # 2022-09-01 14:18:05
    ## TODO: for discord, get time in their local timezone with the <t:thing>
    tz = time.tzname[time.daylight]
    return time.strftime('%Y-%m-%d %Hh %Mm', time.localtime(epoch_seconds)) + f" {tz}"

def get_nft_stats():
    response = httpx.post(API_COLLECTION_DATA, json=nft_stats, headers=headers)
    data = response.json()
    print(data.keys())

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

def get_latested_sales():
    # make a post requests to API with params
    response = httpx.post(API, json=recently_sold, headers=headers)
    data = response.json()['nfts']


    for nft in data:
        name = nft['name']
        num_likes = len(nft['likes'])
        rank = nft['rank']
        coll_name = nft['coll_name']
        listing_link = LISTING_LINK.replace("{ID}", nft['id'].split(" ")[1])

        # lat sold
        scrt_price = nft['last_sold']['price']
        dollar_price = nft['last_sold']['dollar_price']
        timestamp = int(nft['last_sold']['timestamp'])/1_000
        # human_timestamp = epoch_to_human(timestamp)
        url = nft['thumbnail'][0]['url']

        print(f"COLLECTION: {coll_name} -> {name} Rank #{rank} likes:{num_likes} scrt:{scrt_price} ${dollar_price}. Image: {url}")

        stats = get_nft_stats()                

        # print(nft.keys())        
        discord_notification(
            webook_url=WEBHOOK_URL,
            title=f"PURCHASE:\n{name} Rank #{rank}", 
            description=f"", 
            color=os.getenv("COLOR", "ffffff").replace("#", ""), 
            values={
                "LINK": [listing_link, True],
                "SCRT": [f"{scrt_price}\t(${dollar_price})", False],                
                "LIKES": [f"+{num_likes}", False],
                "FLOOR": [f"${stats['floor']}", False],
                "TIME SOLD": [f"<t:{int(timestamp)}>", False],
            }, 
            thumbnail=os.getenv("THUMBNAIL_IMAGE", ""), 
            image=url, 
            footerText=""
        )
        input("\n\n\n")


get_latested_sales()