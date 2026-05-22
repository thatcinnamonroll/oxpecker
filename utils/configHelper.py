from playwright.sync_api import sync_playwright
from playwright._impl._errors import TimeoutError as playwrightTimeout
import json
import time
import requests
from bs4 import BeautifulSoup
import json
from utils.scrape import scrapeProfileInfo

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
