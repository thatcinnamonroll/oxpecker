import json
from playwright.sync_api import sync_playwright
from utils.scrape import scrapeFromTwitter

with open(".data/userFingerprint.json","r") as fingerPrintFile:
    userFingerpirintData = json.load(fingerPrintFile)

with open(".data/userFollowed.json","r") as followedProfilesFile:
    userFollowedData = json.load(followedProfilesFile)
    userFollowed = userFollowedData.get("accounts")
    
with sync_playwright() as playwright:
    scrapedData = scrapeFromTwitter(playwright,userFingerpirintData,userFollowed)
    print("Done Scraping :D")

    # i know this is silly but it's just for test
    with open(".test/index.html","w") as firstIndex:
        firstIndex.write(scrapedData[0])

    with open(".test/index2.html","w") as secondIndex:
        secondIndex.write(scrapedData[1])

    print("exiting")

