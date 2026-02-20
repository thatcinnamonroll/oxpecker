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

        # reading text in tweet
        articleSoup = BeautifulSoup(strArticle,"html.parser")
        tweetText = articleSoup.find("div", {"data-testid":"tweetText"})
        tweetList = []
        strTweetText = str(tweetText)
        tweetTextSoup = BeautifulSoup(strTweetText,"html.parser")
        # that span holds clean text of tweet
        textInTweet = tweetTextSoup.findAll("span",{"class":"css-1jxf684 r-bcqeeo r-1ttztb7 r-qvutc0 r-poiln3"})
        strTextInTweet = str(textInTweet)
        rmTagsSoup = BeautifulSoup(strTextInTweet,"html.parser")
        cleanTweet = rmTagsSoup.get_text()
        tweetList.append(cleanTweet)
        tweetStr = "".join(tweetList)

        # reading tweet author
        tweetAuthorBarSoup = BeautifulSoup(strArticle,"html.parser")
        tweetAuthorBar = tweetAuthorBarSoup.find("div",{"class":"css-175oi2r r-k4xj1c r-18u37iz r-1wtj0ep"})
        strTweetAuthorBar = str(tweetAuthorBar)
        authorTweetSoup = BeautifulSoup(strTweetAuthorBar,"html.parser")
        authorTweet = authorTweetSoup.find("span",{"class":"css-1jxf684 r-bcqeeo r-1ttztb7 r-qvutc0 r-poiln3"})
        authorTweetText = authorTweet.get_text()

        # reading added media (photos as of right now)
        tweetMediaSoup = BeautifulSoup(strArticle,"html.parser")
        tweetMediaImgList = tweetMediaSoup.findAll("img",{"alt":"Image"})
        tweetMediaList = []
        for image in tweetMediaImgList:
            tweetMediaList.append(image['src'])

        # adding to tweets list
        tweet = {}
        tweet["text"] = tweetStr
        tweet["author"] = authorTweetText
        tweet["media"] = tweetMediaList

        tweets.append(tweet)

    with open(f".test/scrapedDataOf{account}.txt","w") as scrapedFile:
        scrapedFile.write(str(tweets))
    context.close()
    browser.close()

    return accHtml
