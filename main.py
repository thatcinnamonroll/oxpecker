import json
from playwright.sync_api import sync_playwright
from utils.scrape import scrapeFromTwitter

with open(".data/userFingerprint.json","r") as fingerPrintFile:
    userFingerpirintData = json.load(fingerPrintFile)

with open(".data/userFollowed.json","r") as followedProfilesFile:
    userFollowedData = json.load(followedProfilesFile)
    userFollowed = []
    for account in userFollowedData:
        userFollowed.append(account)
    
with sync_playwright() as playwright:
    scrapeFromTwitter(playwright,userFingerpirintData,userFollowed)
    print("Done Scraping :D")

