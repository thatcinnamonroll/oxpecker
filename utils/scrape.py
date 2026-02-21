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
#        "text": str, # text in tweet
#        "author": str, # author bc tweet can be reposted from someone
#        "media": [],  # multimedia urls
#        "isRetweet": bool,  # is that tweet is a retweet
#        "isPinned": bool } # is that tweet pinned

    for article in articlesHtml:
        strArticle = str(article)

        # reading text in tweet
        articleSoup = BeautifulSoup(strArticle,"html.parser")
        tweetText = articleSoup.find("div", {"data-testid":"tweetText"})
        tweetList = []
        strTweetText = str(tweetText)
        tweetTextSoup = BeautifulSoup(strTweetText,"html.parser")
        textInTweet = tweetTextSoup.findAll("span",{"class":"css-1jxf684 r-bcqeeo r-1ttztb7 r-qvutc0 r-poiln3"})   # that span holds clean text of tweet
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

        # cheking is it retweet or pinned post
        isRetweet = False
        isPinned = False
        reTweetAndPinnedBarSoup = BeautifulSoup(strArticle,"html.parser")
        reTweetAndPinnedBar = reTweetAndPinnedBarSoup.find("div",{"class":"css-175oi2r"})
        strReTweetAndPinnedBar = str(reTweetAndPinnedBar)

        upperTweetBarSoup = BeautifulSoup(strReTweetAndPinnedBar,"html.parser")
#        if upperTweetBarSoup.findAll("div",{"id":"id__u731578ebyt"}) is not []: # this div only exists for pinned tweets
#            isPinned = True
#
#        if upperTweetBarSoup.findAll("span",{" data-testid":"socialContext"}) is not []:
#            isRetweet = True

        # adding to tweets list
        tweet = {}
        tweet["text"] = tweetStr
        tweet["author"] = authorTweetText
        tweet["media"] = tweetMediaList
        tweet["isRetweet"] = isRetweet
        tweet["isPinned"] = isPinned

        tweets.append(tweet)

    with open(f".test/scrapedDataOf{account}.txt","w") as scrapedFile:
        scrapedFile.write(str(tweets))
    context.close()
    browser.close()

    return accHtml
