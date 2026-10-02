import time
from bs4 import BeautifulSoup
import json
from playwright._impl._errors import TimeoutError as playwrightTimeout

def getPfpUrl(account,page,debugMode):
    # getting page with profile pic
    page.get_by_role("link", name="Opens profile photo").click()
    time.sleep(1)
    pfpPageHtml = page.content()
    page.get_by_role("button", name="Close").click()
    time.sleep(0.5)

    pfpSoup = BeautifulSoup(pfpPageHtml,"html.parser")
    pfpDiv = pfpSoup.find("div",{"class":"css-g5y9jx r-1mlwlqe r-1udh08x r-417010 r-aqfbo4 r-n1ft60 r-gf0ln r-agouwx r-1p0dtai r-16l9doz r-1d2f490 r-pm9dpa r-dnmrzs r-u8s1d r-zchlnj r-ipm5af r-iyfy8q r-sdzlij r-1fdo3w0"})

    pfpDivSoup = BeautifulSoup(str(pfpDiv),"html.parser")
    pfpImg = pfpDivSoup.find("img",{"class":"css-9pa8cd"})
    pfpUrl = pfpImg["src"]

    if debugMode:
        with open(f".cache/test/indexOfPfp{account}.html","w") as pfpIndex:
            pfpIndex.write(pfpPageHtml)

    return pfpUrl

def loadMoreTweets(page):
    # scrolling so browser loads more content
    scrollNum = 0
    while scrollNum < 20:
        page.mouse.wheel(0,120)
        time.sleep(0.3)
        scrollNum += 1

    # clicking "show more" buttons to get full tweets
    showMoreButtons = page.get_by_test_id("tweet-text-show-more-link").all()
    for button in showMoreButtons:
        try:
            button.click()
        except playwrightTimeout:
            continue
        time.sleep(0.1)

def sortTweetsAndRetweets(account,metadata):
    with open(f".cache/scrape/{account}-tweets.json","r") as tweetsFile:
        originalTweets = json.load(tweetsFile)
    with open(f".cache/scrape/{account}-retweets.json","r") as retweetsFile:
        retweets = json.load(retweetsFile)
    tweets = originalTweets + retweets
    # releace ram
    originalTweets = None
    retweets = None

    # sort tweets by post time
    sortedTweets = sorted(tweets, key=lambda x: x["time"])

    # releace ram
    tweets = None

    accountData = {"metadata":metadata,"tweets":sortedTweets}
    sortedTweets = None

    with open(f".cache/scrape/{account}-data.json","w") as scrapedFile:
        scrapedFile.write(json.dumps(accountData, indent=4)) # indent=4 to make json look pretty
    accountData = None
