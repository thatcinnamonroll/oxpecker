from playwright.async_api import sync_playwright
context.storage_state(path="file")
# in production :)
def makeTwitterCacheFile():
    with sync_playwright() as playwright:
        browser = playwright.firefox.launch()
        context = browser.new_context()
        page = context.new_page()
