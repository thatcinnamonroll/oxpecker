import time
from playwright.sync_api import Playwright
from playwright._impl._errors import TimeoutError as playwrightTimeout
import random
from bs4 import BeautifulSoup

def scrapeFromTwitter(playwright:Playwright,fingerPrintDict,accountsList,nitter):
    browser = playwright.firefox.launch()
    context = browser.new_context(geolocation=fingerPrintDict.get("geolocation"), locale=fingerPrintDict.get("locale"), permissions=fingerPrintDict.get("permissions"), storage_state=fingerPrintDict.get("storage_state"), timezone_id=fingerPrintDict.get("timezone_id"), user_agent=fingerPrintDict.get("user_agent"))
    page = context.new_page()

    tweets = {}
    for acc in accountsList:
        tweetList = twitterScraper(page,acc,nitter)
        tweets[acc] = tweetList

    context.close()
    browser.close()

    return tweets

def twitterScraper(page,account,nitter):
    print(f"scraping @{account}")
    page.goto(f"https://x.com/{account}")
    time.sleep(9)
    # scrolling so browser loads more content
    scrollNum = 0
    while scrollNum < 20:
        page.mouse.wheel(0,120)
        time.sleep(0.3)
        scrollNum += 1

    # clicking "show more" buttons to get full tweet
    showMoreButtons = page.get_by_test_id("tweet-text-show-more-link").all()
    for button in showMoreButtons:
        try:
            button.click()
        except playwrightTimeout:
            continue
        time.sleep(0.1)

    accHtml = page.content()
    soup = BeautifulSoup(accHtml,"html.parser")
    articlesHtml = soup.find_all('article')
    # list of all tweets
    tweets = []

    # this is single object in tweets
#    tweet = {
#        "text": str, # text in tweet
#        "author": str, # author bc tweet can be reposted from someone
#        "authorUsername": str, # writers @at
#        "media": [],  # multimedia urls
#        "hasVideo": bool, # does tweet has video in it
#        "isRetweet": bool,  # is that tweet is a retweet
#        "isPinned": bool , # is that tweet pinned
#        "hasRef": bool, # if tweet is refering other tweet this will be true
#        "url": str,  # url to that tweet
#        "tweetId": str } # id of the tweet

    for article in articlesHtml:
        strArticle = str(article)
        articleSoup = BeautifulSoup(strArticle,"html.parser")

        # ad detector
        menuButton = articleSoup.find("div",{"class":"css-175oi2r r-1kkk96v"})
        strMenuButton = str(menuButton)
        adDetectSoup = BeautifulSoup(strMenuButton,"html.parser")
        if adDetectSoup.findAll("span",{"class":"css-1jxf684 r-bcqeeo r-1ttztb7 r-qvutc0 r-poiln3"}):
            print("Ad detected in feed, skiping that post")
            continue

        # reading text in tweet
        tweetText = articleSoup.find("div", {"data-testid":"tweetText"})
        tweetList = []
        strTweetText = str(tweetText)
        tweetTextSoup = BeautifulSoup(strTweetText,"html.parser")
        for tag in tweetTextSoup.children:
            text = tag.getText()
            formatedText = text.replace("@",f"{nitter}/")
            tweetList.append(formatedText)
        tweetStr = "".join(tweetList)

        # reading tweet author
        tweetAuthorBar = articleSoup.find("div",{"class":"css-175oi2r r-k4xj1c r-18u37iz r-1wtj0ep"})
        strTweetAuthorBar = str(tweetAuthorBar)
        authorTweetSoup = BeautifulSoup(strTweetAuthorBar,"html.parser")
        authorTweet = authorTweetSoup.find("span",{"class":"css-1jxf684 r-bcqeeo r-1ttztb7 r-qvutc0 r-poiln3"})
        authorTweetText = authorTweet.get_text()

        # reading added media (photos as of right now)
        tweetMediaImgList = articleSoup.findAll("img",{"alt":"Image"})
        tweetMediaList = []
        for image in tweetMediaImgList:
            tweetMediaList.append(image['src'])

        # checking if tweet has video
        # the original plan was video repost support but they are kinda hard to code since i can't just take
        # vid url, at least i dont't think so
        hasVideo = False
        if articleSoup.findAll("div",{"data-testid":"videoPlayer"}):
            hasVideo = True

        # cheking is it retweet or pinned post
        isRetweet = False
        isPinned = False
        reTweetAndPinnedBar = articleSoup.find("div",{"class":"css-175oi2r"})
        strReTweetAndPinnedBar = str(reTweetAndPinnedBar)

        upperTweetBarSoup = BeautifulSoup(strReTweetAndPinnedBar,"html.parser")
        if upperTweetBarSoup.findAll("div",{"data-testid":"socialContext"}): # this div only exists for pinned tweets
            isPinned = True

        if upperTweetBarSoup.findAll("span",{"data-testid":"socialContext"}): # this span only exists in that div when tweet is reposted
            isRetweet = True

        # getting tweet url
        tweetMetadataBar = articleSoup.find("div",{"class":"css-175oi2r r-zl2h9q"})
        strTweetMetadataBar = str(tweetMetadataBar)
        tweetPostDateSoup = BeautifulSoup(strTweetMetadataBar,"html.parser")
        tweetPostDate = articleSoup.find("a",{"class":"css-146c3p1 r-bcqeeo r-1ttztb7 r-qvutc0 r-37j5jr r-a023e6 r-rjixqe r-16dba41 r-xoduu5 r-1q142lx r-1w6e6rj r-9aw3ui r-3s2u2q r-1loqt21"})
        try:
            tweetUrl = tweetPostDate["href"]
        except TypeError:
            tweetUrl = None

        # checking if tweet is refering to another tweet
        hasRef = False
        tweetRef = articleSoup.find("div",{"class":"css-175oi2r r-adacv r-1udh08x r-1ets6dv r-1867qdf r-rs99b7 r-o7ynqc r-6416eg r-1ny4l3l r-1loqt21"})
        if tweetRef is not None:
            hasRef = True

        # separating username and tweet id from url
        listFromUrl = tweetUrl.split("/")
        # this returns a list that looks like this ["","username","status","tweetID"]
        tweetAuthorUsername = listFromUrl[1]
        tweetId = listFromUrl[3]

        # adding to tweets list
        tweet = {}
        tweet["text"] = tweetStr
        tweet["author"] = authorTweetText
        tweet["authorUsername"] = tweetAuthorUsername
        tweet["media"] = tweetMediaList
        tweet["hasVideo"] = hasVideo
        tweet["isRetweet"] = isRetweet
        tweet["isPinned"] = isPinned
        tweet["hasRef"] = hasRef
        tweet["url"] = tweetUrl
        tweet["id"] = tweetId

        tweets.append(tweet)

    with open(f".test/scrapedDataOf{account}.txt","w") as scrapedFile:
        scrapedFile.write(str(tweets))

    with open(f".test/indexOf{account}.html","w") as firstIndex:
        firstIndex.write(accHtml)

    return tweets



