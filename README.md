# stashh-bot
(built initially for racoon-supply)

![image](https://github.com/Reecepbcups/stashh-bot/assets/31943163/ede459c0-616b-4fe6-8b18-3097faf85ef8)
![image](https://github.com/Reecepbcups/stashh-bot/assets/31943163/0b85430f-c799-4089-b9ce-77536a7c8d2c)



Issues? Contact Reece#3370 or create an issue in the repo.

### Setup
```bash
cp .env.example .env
# Fill out the data as you need for your collection

# Using a crontab / system service, set it up to run every X minutes. 5 minute Example:
# EDITOR=nano crontab -e
# */5 * * * * cd /home/user/stashh-bot && python3 src/bot.py
# (ctrl+x to exit)
```
