from playwright.sync_api import sync_playwright
from playwright._impl._errors import TimeoutError as playwrightTimeout
import json
import time
import requests
from bs4 import BeautifulSoup
import secrets
import json

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

def makeMastodonAccount(username,accountSettings,botUrl,botToken):
    shouldAskForPassword = accountSettings["userManagesPasswords"]
    email = f"{username}{accountSettings["emailPrefix"]}"
    if shouldAskForPassword:
        password = input(f"Type password for bot account posting from twitter profile @{username}: ")
    else:
        password = secrets.token_urlsafe(40)

    header = {'Authorization': f'Bearer {botToken}',
                     'content-type':'application/json'}

    data = {
        "reason":f"Submitted by oxpecker bot this account will be used to repost stuff from twitter account @{username}",
        "username":username,
        "email":email,
        "password":password,
        "agreement":True
        }

    requestData = json.dumps(data).encode("utf-8")

    response = requests.post(f"{botUrl}/api/v1/accounts",data=requestData,headers=header)
    time.sleep(1) # wait for the request

    if response.status_code == 200:
        responseData = response.json()
        botToken = responseData["access_token"]
        print(f"Bot account for @{username} was successfully subbmited")
        return botToken
    else:
        print(f"Something went wrong, Error code: {response.status_code}")
        return None

def setupMastodonAccount(token,url,fingerprint):
    with sync_playwright() as playwright:
        browser = playwright.firefox.launch()
        context = browser.new_context(geolocation=fingerprint.get("geolocation"), locale=fingerprint.get("locale"), permissions=fingerprint.get("permissions"), storage_state=fingerprint.get("storage_state"), timezone_id=fingerprint.get("timezone_id"), user_agent=fingerprint.get("user_agent"))
        page = context.new_page()




    header = {'Authorization': f'Bearer {botToken}',
                     'content-type':'application/json'}

    data = {
        "reason":f"Submitted by oxpecker bot this account will be used to repost stuff from twitter account @{username}",
        "username":username,
        "email":email,
        "password":password,
        "agreement":True
        }

    requestData = json.dumps(data).encode("utf-8")

    response = requests.post(f"{botUrl}/api/v1/accounts",data=requestData,headers=header)
    time.sleep(1) # wait for the request



