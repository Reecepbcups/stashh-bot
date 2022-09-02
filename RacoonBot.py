import httpx, string, random, time
# from notifications import discord_notification

API = "https://stashh.io/nfts/get"
API_COLLECTION_DATA = "https://stashh.io/collection/fetch"

RAC_CONTRACT = "secret1dvd46mkjr8s4cl2czv03h9y82heeefc0hzlrat"
LIST_LINK = "https://stashh.io/asset/racn/RACOON%20{ID}"
WEBHOOK_URL = "https://discord.com/api/webhooks/1015253850892030052/0zT4dKSw6OuaRTWE1HzY04Ek7Et2iq-GbaiLliA8b7NLGWrQ2I2TN4hfKcStKXkHSe2a"

headers = {
    # user agent
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Mobile Safari/537.36",
    "accept": "application/jsopyhonn, text/plain, */*",
    "accept-enconding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.5",
    "scheme": "https",
    "authorization": "Bearer " + '''eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI2MmRlY2ZmMDg2OWQxMjA1MTMyM2I3M2QiLCJhZGRyZXNzIjoic2VjcmV0MXlkemFzNWtlZjRuaHJha3d0NmMwZzVzYTRmNjY1cGt2bjVzMnZmIiwiYWNjZXNzIjowLCJjcmVhdGVkX2F0IjoxNjU4NzY5MzkyMzgzLCJsYXN0X2Nvbm5lY3RlZCI6MTY2MjAxMDA0NjU2OCwicGVybWl0IjoiZDBlMWJhYzFkYzMwMzQ3ZTE0N2FmZDExMTc4NGZlMmI4YjIwODcyM2M1NmUxMGU4Mjg4M2ZkMmVmNzRjNzJhNDAxNzNiNTYwYmYzOGM2ZTk1YTMxYTdlODFjZjZlOWI4NDAxMWM4MWZiYmZmYjE3YWQyYTUwMmEyZjk4NGMzN2EiLCJ1bnNlZW5fbm90aWZpY2F0aW9ucyI6MCwidW5zZWVuX3NhbGVzIjowLCJhdXRoZW50aWNhdGVkIjp0cnVlLCJiYW5uZXIiOiJodHRwczovL3N0YXNoaGFwcHN0b3JhZ2UuYmxvYi5jb3JlLndpbmRvd3MubmV0L3Byb2ZpbGUtYXNzZXRzL3NlY3JldDF5ZHphczVrZWY0bmhyYWt3dDZjMGc1c2E0ZjY2NXBrdm41czJ2Zl9iYW5uZXJfMTY1ODc2OTUwODMwOC5qcGciLCJkZXNjcmlwdGlvbiI6IkNyYWZ0IEVjb25vbXkgVGVjaG5va2luZyAoQ1RPKSwgQmxvY2tjaGFpbiwgJiBJbnRlZ3JhdGlvbiIsImRpc2NvcmQiOiJSZWVjZSMzMzcwIiwiZ2l0aHViIjoiaHR0cHM6Ly9naXRodWIuY29tL3JlZWNlcGJjdXBzIiwiaW1hZ2UiOiJodHRwczovL3N0YXNoaGFwcHN0b3JhZ2UuYmxvYi5jb3JlLndpbmRvd3MubmV0L3Byb2ZpbGUtYXNzZXRzL3NlY3JldDF5ZHphczVrZWY0bmhyYWt3dDZjMGc1c2E0ZjY2NXBrdm41czJ2Zl9pY29uXzE2NTg3Njk1MDgyNzQuanBnIiwibmFtZSI6IlJlZWNlcGJjdXBzIiwidHdpdHRlciI6IkBSZWVjZXBiY3Vwc18iLCJ1cGRhdGVkX2F0IjoxNjU4NzY5NTA4NTM5LCJ3ZWJzaXRlcyI6WyJodHRwczovL3JlZWNlLnNoIl0sIndoaXRlbGlzdGVkIjpmYWxzZSwiaWF0IjoxNjYyMDEwNjAyLCJleHAiOjE2NjIwOTcwMDJ9.tA62kFla4dlpKXxRkiGpdi1S6eIcWX1pGBmxBg7VlsM''',
    "content-type": "application/json",
    "origin": "https://stashh.io",
    "request-id": "42f7e6af08c643d3ad12e0fcbb2522c6.463e3ce868954c2d",
    "sec-ch-ua": '.Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
    "sec-ch-ua-mobile": "?1",
    "sec-ch-ua-platform": "Android",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "request-context": "appId=cid-v1:a2219503-e743-4f47-91d6-aabeeb1605c0",
    "sec-fetch-site": "same-origin",
    "traceparent": "00-42f7e6af08c643d3ad12e0fcbb2522c6-463e3ce868954c2d-01",
    "cookie": '''ARRAffinity=ee66be9bf3659f9f4e079e865094addeb6f1b63b4dfd9367cea55483841c9c68; ARRAffinitySameSite=ee66be9bf3659f9f4e079e865094addeb6f1b63b4dfd9367cea55483841c9c68; ai_user=w93DgTZGtBiBZDQLlPC+zO|2022-09-01T05:54:23.665Z; ai_session=N/ZgqinNsVc2+tY8JhiOzk|1662011663815|1662011663815; _clck=1ngcawr|1|f4i|0; __cf_bm=tOuwydaNhhcHnS3WXLgS50kEOflxNkjaDHN3PUXA2Os-1662011653-0-AdnJJJSGPMUj82k1v+nHMJmxAMMylKGA0VwRAF84a+flW66wtTTUvhlbYkYib0T+agWERwuzQEI5kY1+oTCLWX5L789TFMcnpMJoMB83YL/rXu6K9UAwLJ4ROLRMFxmA6A==; _clsk=jg46zn|1662011670008|2|1|d.clarity.ms/collect'''
} 

# recently sold nfts
recently_sold = {
    "params":  {
        "limit":24,"skip":0,
        "collections":["secret1dvd46mkjr8s4cl2czv03h9y82heeefc0hzlrat"],
        "is_badge":False,"sort_by":"sold_date","ascending":False,"is_spam":False,"query_id":"Y6FkHqytBfuH9eqaAaRD"
    }
}
nft_stats = {
    "address": "racn"
}

# TOO: floor price & stuffs

# get a radno random string of a-zA-Z0-9 length 20
def get_random_string(length):
    letters = string.ascii_letters + string.digits
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

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
        "min": data['min'],
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
        listing_link = LIST_LINK.replace("{ID}", nft['id'].split(" ")[1])

        # lat sold
        scrt_price = nft['last_sold']['price']
        dollar_price = nft['last_sold']['dollar_price']
        timestamp = int(nft['last_sold']['timestamp'])/1_000
        human_timestamp = epoch_to_human(timestamp)
        url = nft['thumbnail'][0]['url']

        print(f"COLLECTION: {coll_name} -> {name} Rank #{rank} likes:{num_likes} scrt:{scrt_price} ${dollar_price} time:{human_timestamp}. Image: {url}")

        # print(nft.keys())

        input("\n\n\n")
        # discord_notification(
        #     webook_url=WEBHOOK_URL,
        #     title=f"NEWEST SELL", 
        #     description=f"{name}, Rank #{rank}", 
        #     color="ffffff", 
        #     values={
        #         "LINK": [listing_link, True],
        #         "SCRT": [scrt_price, True],
        #         "USD": [dollar_price, True],
        #     }, 
        #     thumbnail="", 
        #     image=url, 
        #     footerText=""
        # )