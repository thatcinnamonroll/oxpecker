from playwright.sync_api import sync_playwright
from playwright._impl._errors import TimeoutError as playwrightTimeout
import json
import time

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


