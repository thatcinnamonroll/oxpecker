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

def insertAuthTokenCookie(auth_token):
    # all val names here are the same as vals in auth_token cookie
    name = "auth_token"
    domain = ".x.com"
    path = "/"
    httpOnly = True
    secure = True
    sameSite = "None"
    value = auth_token["value"]
    expires = int(auth_token["expires"])

    auth_token_cookie = {}
    auth_token_cookie["name"] = name
    auth_token_cookie["domain"] = domain
    auth_token_cookie["value"] = value
    auth_token_cookie["path"] = path
    auth_token_cookie["httpOnly"] = httpOnly
    auth_token_cookie["expires"] = expires
    auth_token_cookie["secure"] = secure
    auth_token_cookie["sameSite"] = sameSite

    with open(".data/storage.json","r") as storageFile:
        storage = json.load(storageFile)
        cookiesList = storage["cookies"]
        cookiesList.append(auth_token_cookie)
        storage["cookies"] = cookiesList
    with open(".data/storage.json","w") as storageFile:
        storageJson = json.dumps(storage,indent=4)
        storageFile.write(storageJson)

    print("Cookies saved!")

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

def setupSettingsFile(geolocale,locale,timezoneId,user_agent,nitter,mastodon,waitTime):
    with open(".data/userSettings.json","r") as settingsFile:
        settings = json.load(settingsFile)

        latitude = geolocale[0]
        longitude = geolocale[1]

        settings["fingerprint"]["geolocation"]["latitude"] = float(latitude)
        settings["fingerprint"]["geolocation"]["longitude"] = float(longitude)
        settings["fingerprint"]["locale"] = locale
        settings["fingerprint"]["timezone_id"] = timezoneId
        settings["fingerprint"]["user_agent"] = user_agent
        settings["nitter"] = nitter
        settings["mastodon"] = mastodon
        settings["waitTime"] = waitTime

    with open(".data/userSettings.json","w") as settingsFile:
        settingsJson = json.dumps(settings,indent=4)
        settingsFile.write(settingsJson)
    print("Settings saved")

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
