# racoon-supply-stashh-bot

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