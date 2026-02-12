import time
from playwright.sync_api import Playwright
import random

def scrapeFromTwitter(playwright: Playwright,fingerPrintDict,accountsList):
    browser = playwright.firefox.launch()
    context = browser.new_context(geolocation=fingerPrintDict.get("geolocation"), locale=fingerPrintDict.get("locale"), permissions=fingerPrintDict.get("permissions"), storage_state=fingerPrintDict.get("storage_state"), timezone_id=fingerPrintDict.get("timezone_id"), user_agent=fingerPrintDict.get("user_agent"))
    page = context.new_page()
    scrapedData = []
    for followed in accountsList:
        print(f"scraping {followed}")
        page.goto(f"https://x.com/{followed}")
        time.sleep(9)
        # scrolling so browser loads more content, random to make it more... human ;)
        randomScrollNum = random.randint(1,3)
        for i in range(randomScrollNum):
            page.keyboard.press("Space")
            time.sleep(1)
        scrapedData.append(page.content())
        time.sleep(3)
    context.close()
    browser.close()

    return scrapedData
