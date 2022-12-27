import httpx, time, os, json

from dotenv import load_dotenv
from utils.notifications import discord_notification
# from utils.time_convert import epoch_to_human

# load env variables
load_dotenv()

# Default endpoints
API = "https://stashh.io/nfts/get"
API_COLLECTION_DATA = "https://stashh.io/collection/fetch"

# Load global needs from env / the .env file
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK", "")
WEBHOOK_URL_AUCTIONS_SALES = os.getenv("DISCORD_WEBHOOK_AUCTIONS_SALES", "")
CONTRACT = os.getenv("CONTRACT", "secret1dvd46mkjr8s4cl2czv03h9y82heeefc0hzlrat")
LISTING_LINK = os.getenv("LISTING_LINK", "https://stashh.io/asset/racn/RACOON%20{ID}")

NOTIFICATIONS = os.getenv("NOTIFICATIONS", "true").lower().startswith("t")
print(f"Notifications: {NOTIFICATIONS}")

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

# recently listed
recently_listed = {
    "params": {
        "limit":200,
        "skip":0,
        "collections":[CONTRACT],
        "is_badge":False, "sort_by":"price", "ascending":True, "is_spam":False, "query_id":"IRvSUyDggMGdibGCi78M"
    }
}

nft_stats = {
    "address": os.getenv("ADDRESS", "racn")
}

## ------------------ File storage ------------------ ##
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

newly_listed_filename = "newly_listed.json"
newly_listed = {}
def load_past_listed_from_file() -> dict:
    global newly_listed
    if not os.path.exists(newly_listed_filename):
        with open(newly_listed_filename, 'w') as f:
            json.dump({}, f)
    with open(newly_listed_filename, 'r') as f:
        newly_listed = json.load(f)       
    return newly_listed
def _save_listed() -> None:
    if len(newly_listed) > 0:
        with open(newly_listed_filename, 'w') as f:
            json.dump(newly_listed, f)
def update_nft_new_listing(nft_id: str, listed_time: int, is_auction: bool):
    global newly_listed
    newly_listed[nft_id] = {
        "timestamp": listed_time, # epoch in seconds
        "is_auction": is_auction
    }
    _save_listed()
## ----------------- /File storage ------------------ ##



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
        rank = nft['rank']
        coll_name = nft['coll_name']
        listing_link = LISTING_LINK.replace("{ID}", nft['id'].split(" ")[1])

        # lat sold
        scrt_price = nft['last_sold']['price']
        dollar_price = nft['last_sold']['dollar_price']
        timestamp = int(int(nft['last_sold']['timestamp'])/1_000)
        # human_timestamp = epoch_to_human(timestamp)
        url = nft['thumbnail'][0]['url']
        # print(f"COLLECTION: {coll_name} -> {name} Rank #{rank} scrt:{scrt_price} ${dollar_price}. Image: {url}")

        # check if the _id is in the past_sold dict, if so, check that the timestamp is newer. If it is not, continue to next check
        if _id in past_sold:
            if timestamp <= past_sold[_id]["timestamp"]:
                continue
        else:
            update_nft_sell_date(_id, timestamp, scrt_price, dollar_price)
            
        # if is first run, run this here then comment out. Set limit for most recent sold to 500
        # update_nft_sell_date(_id, timestamp, scrt_price, dollar_price); continue        
        lastScrtAmt = float(past_sold[_id]['scrt_amt'])
        lastDollarAmt = float(past_sold[_id]['dollar_amt'])

        scrt_difference = round(float(scrt_price) - lastScrtAmt, 2)
        dollar_difference = round(float(dollar_price) - lastDollarAmt, 2)

        scrt_percent = round((scrt_difference / lastScrtAmt) * 100, 2)
        dollar_percent = round((dollar_difference / lastDollarAmt) * 100, 2)

        sign = "+" if scrt_difference > 0 else "" # auto does negative        

        if NOTIFICATIONS:
            discord_notification(
                webook_url=WEBHOOK_URL,
                title=f"PURCHASE:\n{name} Rank #{rank}", 
                description=f"", 
                color=os.getenv("COLOR", "ffffff").replace("#", ""), 
                values={
                    "LINK": [listing_link, True],
                    "SCRT": [f"{scrt_price}\t(${dollar_price})", False],
                    "Change Since Last Sale": [f"{sign}{scrt_difference}SCRT ({sign}{scrt_percent}%)\n{sign}${dollar_difference} ({sign}{dollar_percent}%)", False],                    
                    "FLOOR / AVG $": [f"Floor: ${stats['floor']}\nAverage: {stats['avg_dollar']}", False],
                    "TIME SOLD": [f"<t:{int(timestamp)}>\n(<t:{int(timestamp)}:R>)", False],
                }, 
                thumbnail=os.getenv("THUMBNAIL_IMAGE", ""), 
                image=url, 
                footerText=""
            )            
            time.sleep(1.3) # discord rate limit

        update_nft_sell_date(_id, timestamp, scrt_price, dollar_price)


# TODO: clean up this rats nest, move to its own class probably
def get_newest_listings():
    response = httpx.post(API, json=recently_listed, headers=headers)
    data = response.json()
    # total_for_sale = data['total']    

    for nft in data['nfts']:
        name = str(nft['name'])
        
        last_sold = nft['last_sold'] # none if none
        if last_sold is not None:
            last_sold_time = int(int(nft['last_sold']['timestamp'])/1_000)
            last_sold_scrt = float(nft['last_sold']['price'])
            last_sold_dollar = float(nft['last_sold']['dollar_price'])

        on_sale = bool(nft['listing']['on_sale']) # boolean

        listing_link = LISTING_LINK.replace("{ID}", nft['id'].split(" ")[1])
        
        dollar_price = float(nft['listing']['dollar_price']) # price in USD
        scrt_price = float(nft['listing']['price']) # price in SCRT
        listed_on = int(int(nft['listing']['listed_on'])/1_000) # epoch in seconds
        closes_at = int(int(nft['listing']['closes_at'])/1_000) # if this is for sale, it is ~100 years out

        url = str(nft['thumbnail'][0]['url'])
        rank = int(nft['rank'])

        is_auction = nft['listing']['is_auction'] # boolean
        buy_now_price = float(nft['listing']['buy_now_price']) # price in SCRT
        has_bids = bool(nft['listing']['has_bids']) # boolean
                

        is_whitelisted = False        
        if 'is_whitelisted' in nft['listing']:
            is_whitelisted = nft['listing']['is_whitelisted'] # boolean

        num_bids = 0
        if num_bids in nft['listing']:
            num_bids = int(nft['listing']['num_bids'])

        # if not is_auction: # TODO: debuging only just to get an auction
        #     continue

        # print(f"Name: {name} Rank: {rank} On Sale: {on_sale} Listed On: {listed_on} Closes At: {closes_at} Price: {scrt_price}SCRT ${dollar_price} Image: {url}")
        # print(f"is_auction {is_auction} buy_now_price {buy_now_price} has_bids {has_bids} is_whitelisted {is_whitelisted} num_bids {num_bids}")        
        # input()

        # if rac has been sold before, ensure its a newer sell than last time.
        if name in newly_listed:
            if listed_on <= newly_listed[name]["timestamp"]:
                continue  
        else:
            update_nft_new_listing(nft['id'], listed_on, is_auction)                  

        if is_whitelisted: # if its whitelisted, other can buy so dont announce it.
            update_nft_new_listing(nft['id'], listed_on, is_auction)
            continue

        # if its an auction, give auction data
        if is_auction:
            auction_values = {
                "LINK": [listing_link, True],
                "Listed at": [f"<t:{int(listed_on)}> (<t:{int(listed_on)}:R>)", False],
                "Current Bid Price": [f"{scrt_price}\t(${dollar_price})", False],
            }            
            if buy_now_price > 0:
                auction_values["Buy Now:"] = [f"{buy_now_price} SCRT", False]
            if has_bids > 0:
                auction_values["Bids:"] = [f"{num_bids}", False]
            if last_sold is not None:
                auction_values["Last Sold: "] = [f"<t:{int(last_sold_time)}>\nFor: {last_sold_scrt}SCRT (${last_sold_dollar})", True]                                

            if NOTIFICATIONS:
                discord_notification(
                    webook_url=WEBHOOK_URL_AUCTIONS_SALES,
                    title=f"AUCTION:\n{name} Rank #{rank}", 
                    description=f"Bid on this NFT before the time runs out!", 
                    color=os.getenv("AUCTION_COLOR", "ffffff").replace("#", ""), 
                    values=auction_values, 
                    thumbnail=os.getenv("THUMBNAIL_IMAGE", ""), 
                    image=url, 
                    footerText=""
                )
                time.sleep(1.2)
        else:
            forsale_values = {
                "LINK": [listing_link, True],
                "Price": [f"{scrt_price}SCRT\t(${dollar_price})", False],             
            }  
            if last_sold is not None:
                last_sold = _getLastSoldData(last_sold)                
                forsale_values["Last Sold Price"] = [f"{last_sold_scrt} (${last_sold_dollar})", True]   
                forsale_values['Last Sold Time'] = [f"<t:{last_sold['timestamp']}>\n(<t:{last_sold['timestamp']}:R>)", False]            
            
            if NOTIFICATIONS:
                discord_notification(
                    webook_url=WEBHOOK_URL_AUCTIONS_SALES,
                    title=f"FOR SALE:\n{name} Rank #{rank}", 
                    description=f"This RAC is available for direct purchase by anyone.", 
                    color=os.getenv("SALE_COLOR", "ffffff").replace("#", ""), 
                    values=forsale_values, 
                    thumbnail=os.getenv("THUMBNAIL_IMAGE", ""), 
                    image=url, 
                    footerText=""
                )
                time.sleep(1.2)

        update_nft_new_listing(nft['id'], listed_on, is_auction)


def _getLastSoldData(last_sold: dict):    
    return {
        "byName": last_sold.get('byName', ""), 
        "by": last_sold.get('by', ""), 
        "price": last_sold.get('price', -1), 
        "usd": last_sold.get('dollar_price', -1), 
        "timestamp": int(int(last_sold.get("timestamp", -1))/1_000)
    }


if __name__ == "__main__":
    load_nft_times_from_file() # load past sold NFTs
    load_past_listed_from_file() # load listings & see which are new listings

    if len(WEBHOOK_URL) > 0:
        get_latest_sales()
    if len(WEBHOOK_URL_AUCTIONS_SALES) > 0:
        get_newest_listings()