import json
import sys
import time
from playwright.sync_api import sync_playwright
from utils.scrape import scrapeFromTwitter
from utils.mastodon import mastodonBot
from utils.util import Bot, downloadImg
from utils.config import BotConfig

try:
    userArgs = sys.argv[1]
except IndexError:
    userArgs = None

print("oxpecker")
print("written by thatcinnamonroll")

if not userArgs == None:
    config = BotConfig()
    print("oxpecker config mode")
    while config._keepConfigLoop:
        print("What do you want to do? (if you dont know type h)")
        userInput = input(": ")
        config.userChoiceParser(userInput)
    sys.exit()

with open(".data/userSettings.json",'r') as fingerPrintFile:
    userSettings = json.load(fingerPrintFile)
    userFingerprint = userSettings["fingerprint"]
    userNitterInstance = userSettings["nitter"]
    userMastodonInstance = userSettings["mastodon"]
    userWaitTime = userSettings["waitTime"]

with open(".data/userFollowed.json","r") as followedProfilesFile:
    userFollowedData = json.load(followedProfilesFile)
    userFollowed = []
    for account in userFollowedData:
        userFollowed.append(account)

with open(".cache/cache.json","r") as cacheFile:
    cacheData = json.load(cacheFile)
    postedTweets = cacheData["posted"]

oxpeckerBot = Bot(userNitterInstance,userMastodonInstance,cacheData,userFollowedData,userWaitTime)
print("ready to work")

# main loop
while True:
    with sync_playwright() as playwright:
        tweetsDict = scrapeFromTwitter(playwright,userFingerprint,userFollowed,userNitterInstance)
        print("Done Scraping :D")

    oxpeckerBot.readAndPost(tweetsDict)

    if oxpeckerBot._waitTime == False: # if wait time will be set to false oxpecker will just turn itself off after one while loop
        sys.exit()

    print("Tweets scraped and posted going to sleep")
    time.sleep(oxpeckerBot._waitTime) # yes i know how it looks, i will make it better
