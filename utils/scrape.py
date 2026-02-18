import time
from playwright.sync_api import Playwright
import random
from bs4 import BeautifulSoup

def scrapeFromTwitter(playwright: Playwright,fingerPrintDict,account):
    browser = playwright.firefox.launch()
    context = browser.new_context(geolocation=fingerPrintDict.get("geolocation"), locale=fingerPrintDict.get("locale"), permissions=fingerPrintDict.get("permissions"), storage_state=fingerPrintDict.get("storage_state"), timezone_id=fingerPrintDict.get("timezone_id"), user_agent=fingerPrintDict.get("user_agent"))
    page = context.new_page()
    scrapedData = []
    print(f"scraping @{account}")
    page.goto(f"https://x.com/{account}")
    time.sleep(9)
    # scrolling so browser loads more content, random to make it more... human ;)
    randomScrollNum = random.randint(1,3)
    for i in range(randomScrollNum):
        page.keyboard.press("Space")
        time.sleep(1)
    accHtml = page.content()
    soup = BeautifulSoup(accHtml,"html.parser")
    articlesHtml = soup.find_all('article')
    # list of all tweets
    tweets = []

    # this is single object in tweets
#    tweet = {
#        "text": "", # text in tweet
#        "author": "", # author bc tweet can be reposted from someone
#        "media": [] } # multimedia urls

    for article in articlesHtml:
        strArticle = str(article)

        articleSoup = BeautifulSoup(strArticle,"html.parser")
        tweetTextHtml = articleSoup.find_all("div", {"data-testid":"tweetText"})
        tweetList = []
        tweetTextList = []

        for tweetText in tweetTextHtml:
            strTweetText = str(tweetText)
            tweetTextSoup = BeautifulSoup(strTweetText,"html.parser")
            textInTweet = tweetTextSoup.findAll("span",{"class":"css-1jxf684 r-bcqeeo r-1ttztb7 r-qvutc0 r-poiln3"})
            tweetList.append(textInTweet)

        for tweetObject in tweetList:
            tweetString = str(tweetObject)
            rmTagsSoup = BeautifulSoup(tweetString,"html.parser")
            cleanTweet = rmTagsSoup.get_text()
            tweetTextList.append(cleanTweet)

        tweetStr = "".join(tweetTextList)
        tweets.append(tweetStr)

    with open(f".test/scrapedDataOf{account}.txt","w") as scrapedFile:
        scrapedFile.write(str(tweets))
    context.close()
    browser.close()

    return accHtml
