import json
from playwright.sync_api import sync_playwright
from utils.scrape import scrapeFromTwitter
from utils.mastodon import mastodonBot

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
    
with sync_playwright() as playwright:
    tweetsDict = scrapeFromTwitter(playwright,userFingerprint,userFollowed,userNitterInstance)
    print("Done Scraping :D")

for followed in tweetsDict:
    botApiKey = userFollowedData[followed]
    tweets = tweetsDict[followed]
    for tweet in tweets:
        tweetStrList = []
        if tweet["id"] in postedTweets:
            continue
        if tweet["isPinned"]:
            continue
        if tweet["isRetweet"]:
            tweetStrList.append(f"[This is retweet from {userNitterInstance}/{tweet["authorUsername"]}]")
        if tweet["hasVideo"]:
            tweetStrList.append("[This tweet has video]")
        tweetStrList.append(f" {tweet["text"]}")
        tweetStrList.append(f"\n [Nitter URL: {userNitterInstance}{tweet["url"]} ]")
        tweetStr = "".join(tweetStrList)
        mastodonBot(botApiKey,userMastodonInstance).post(tweetStr)
        postedTweets.append(tweet["id"])
    with open(".cache/cache.json","w") as cacheFile:
        cacheData["posted"] = postedTweets
        cacheJson = json.dumps(cacheData,indent=4)
        cacheFile.write(cacheJson)

