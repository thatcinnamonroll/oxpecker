from os import name, path
from playwright.sync_api import sync_playwright
import time

def twitterLogin(browser):
    page = browser.new_page()
    time.sleep(2)
    page.get_by_role("textbox").fill()
    page.get_by_role('button', name='Dalej').click()
    time.sleep(2)
    page.get_by_role("password").fill() 
    page.get_by_role("button",name="Zaloguj się").click()
    time.sleep(4)




with sync_playwright() as p:
    browser = p.chromium.launch()
    # page = browser.new_page()
    # page.goto("https://playwright.dev")
    # print(page.content())
    twitterLogin(browser)
    browser.close()

