import json
from playwright.sync_api import sync_playwright
from utils.scrape import scrapeFromTwitter
from utils.mastodon import mastodonBot
from utils.util import Bot

print("oxpecker")
print("written by thatcinnamonroll")

with open(".data/userSettings.json",'r') as fingerPrintFile:
    userSettings = json.load(fingerPrintFile)
    userFingerprint = userSettings["fingerprint"]
    userNitterInstance = userSettings["nitter"]
    userMastodonInstance = userSettings["mastodon"]

with open(".data/userFollowed.json","r") as followedProfilesFile:
    userFollowedData = json.load(followedProfilesFile)
    userFollowed = []
    for account in userFollowedData:
        userFollowed.append(account)

with open(".cache/cache.json","r") as cacheFile:
    cacheData = json.load(cacheFile)
    postedTweets = cacheData["posted"]

oxpeckerBot = Bot(userNitterInstance,userMastodonInstance,cacheData,userFollowedData)
print("ready to work")
    
with sync_playwright() as playwright:
    tweetsDict = scrapeFromTwitter(playwright,userFingerprint,userFollowed,userNitterInstance)
    print("Done Scraping :D")

oxpeckerBot.ReadAndPost(tweetsDict)


