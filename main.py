import json
from playwright.sync_api import sync_playwright
from utils.scrape import scrapeFromTwitter

with open(".data/userSettings.json",'r') as fingerPrintFile:
    userSettings = json.load(fingerPrintFile)
    userFingerprint = userSettings["fingerprint"]

with open(".data/userFollowed.json","r") as followedProfilesFile:
    userFollowedData = json.load(followedProfilesFile)
    userFollowed = []
    for account in userFollowedData:
        userFollowed.append(account)
    
with sync_playwright() as playwright:
    scrapeFromTwitter(playwright,userFingerprint,userFollowed)
    print("Done Scraping :D")

