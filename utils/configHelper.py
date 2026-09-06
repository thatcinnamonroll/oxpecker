from playwright.sync_api import sync_playwright
from playwright._impl._errors import TimeoutError as playwrightTimeout
import json
import time
import requests
from bs4 import BeautifulSoup
import json
from utils.scrape import scrapeProfileInfo
from utils.mastodon import mastodonBot
from utils.util import makeListOfFollowed

def makeTwitterCacheFile():
    with sync_playwright() as playwright:
        browser = playwright.firefox.launch()
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://x.com/")
        time.sleep(9) # waiting so page loads
        # accepting all cookies, so the cookie baner doesn't hide tweets
        try:
            page.get_by_role("button", name="Accept all cookies").click()
            time.sleep(1)
        except playwrightTimeout:
            pass
        context.storage_state(path=".data/storage.json")
        context.close()
        browser.close()

def getUserAgent():
    request = requests.get("https://www.useragents.me/")
    websiteHtml = request.content
    soup = BeautifulSoup(websiteHtml,"html.parser")
    desktopUserAgents = str(soup.find("div",{"id":"most-common-desktop-useragents-json-csv"}))
    scrapeSoup = BeautifulSoup(desktopUserAgents,"html.parser")
    useragentsText = scrapeSoup.find("textarea",{"class":"form-control"}).get_text()
    useragentsList = json.loads(useragentsText)
    listNum = 0
    for agent in useragentsList:
        print(f"{listNum} - {agent["ua"]}")
        listNum += 1
    keepGoing = True
    userSelectedUA = False
    while keepGoing:
        userChoice = int(input("Select which user agent do you want: "))
        try:
            userSelectedUA = useragentsList[userChoice]
        except IndexError:
            print("invalid choice, try again")
        if userSelectedUA:
            keepGoing = False

    userAgent = userSelectedUA["ua"]
    return userAgent

def getInfoAboutTwitterUser(username,fingerprint,shouldAddFooter):
    footer = "[THIS IS NOT OFFICIAL ACCOUNT ITS ONLY A BOT THAT REPOSTS FROM TWITTER/X]"
    with sync_playwright() as playwright:
        browser = playwright.firefox.launch()
        context = browser.new_context(geolocation=fingerprint.get("geolocation"), locale=fingerprint.get("locale"), permissions=fingerprint.get("permissions"), storage_state=fingerprint.get("storage_state"), timezone_id=fingerprint.get("timezone_id"), user_agent=fingerprint.get("user_agent"))
        page = context.new_page()

        page.goto(f"https://x.com/{username}")
        time.sleep(10) # waiting for the page to fully load
        profileHtml = page.content()

        context.close()
        browser.close()

        info = scrapeProfileInfo(profileHtml)

        if shouldAddFooter:
            bioNonFooter = info["bio"]
            bio = bioNonFooter + "\n\n\n" + footer
            info["bio"] = bio

        return info

def postStatus():
    with open(".data/userSettings.json","r") as settingsFile:
        userSettings = json.load(settingsFile)
    token = userSettings["statusAccountToken"]
    mastodonUrl = userSettings["mastodon"]
    debug = userSettings["debugMode"]

    statusBot = mastodonBot(token,mastodonUrl,debug)

    message = ""

    while True:
        print("Write Your message:")
        message = input(": ")
        print("Your message will look like this")
        print(message)
        userChoice = input("Do you want to post it? (y - yes, N - no, e - edit): ")
        if userChoice == "y":
            break
        elif userChoice == "e":
            continue
        else:
            return False

    statusBot.post(message)

def enrollNitter():
    with open(".data/userSettings.json","r") as settingsFile:
        userSettings = json.load(settingsFile)
    nitter = userSettings["nitter"]
    mastodonUrl = userSettings["mastodon"]

    with open(".data/userFollowed.json","r") as followedFile:
        followed = json.load(followedFile)
    followedList = makeListOfFollowed(followed)
    for account in followedList:
        requestHeader = {'Authorization': f'Bearer {followed[account]}'}

        data = {
            "fields_attributes[0][name]":"Official Profile",
            "fields_attributes[0][value]":f"{nitter}/{account}"
        }

        response = requests.patch(f"{mastodonUrl}/api/v1/accounts/update_credentials",data=data,headers=requestHeader)
        time.sleep(2) # wait for request

        if response.status_code == 200:
            responseData = response.json()
            print(f"Nitter enroll for @{account} Done")
        else:
            print(f"Nitter enroll for @{account} Failed, status code: {response.status_code}")

