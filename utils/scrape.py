import time
from playwright.sync_api import Playwright

def scrapeFromTwitter(playwright: Playwright,fingerPrintDict,accountsList):
    browser = playwright.firefox.launch()
    context = browser.new_context(geolocation=fingerPrintDict.get("geolocation"), locale=fingerPrintDict.get("locale"), permissions=fingerPrintDict.get("permissions"), storage_state=fingerPrintDict.get("storage_state"), timezone_id=fingerPrintDict.get("timezone_id"), user_agent=fingerPrintDict.get("user_agent"))
    page = context.new_page()
    scrapedData = []
    for followed in accountsList:
        print(f"scraping {followed}")
        page.goto(f"https://x.com/{followed}")
        time.sleep(9)
        scrapedData.append(page.content())
        time.sleep(3)
    context.close()
    browser.close()

    return scrapedData