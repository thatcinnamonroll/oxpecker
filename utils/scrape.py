import time
from playwright.sync_api import Playwright
from playwright._impl._errors import TimeoutError as playwrightTimeout
import random
from bs4 import BeautifulSoup
import json
import datetime
from utils.scrapeHelper import *

def scrapeProfileInfo(page):
    soup = BeautifulSoup(page,"html.parser")

    # reading displayname
    usernameDiv = soup.find("div",{"class":"css-146c3p1 r-bcqeeo r-1ttztb7 r-qvutc0 r-37j5jr r-adyw6z r-135wba7 r-1vr29t4 r-1awozwy r-6koalj r-1udh08x"})
    usernameDivSoup = BeautifulSoup(str(usernameDiv),"html.parser")
    spanDisplayname = usernameDivSoup.find_all("span",{"class":"css-1jxf684 r-bcqeeo r-1ttztb7 r-qvutc0 r-poiln3"})
    displaynameUnformated = spanDisplayname[1]
    displaynameSoup = BeautifulSoup(str(displaynameUnformated),"html.parser")
    displayname = displaynameSoup.getText()

    # reading account description
    bioDir = soup.find("div",{"data-testid":"UserDescription"})
    bioDirSoup = BeautifulSoup(str(bioDir),"html.parser")
    bioUnformated = bioDirSoup.find("span",{"class":"css-1jxf684 r-bcqeeo r-1ttztb7 r-qvutc0 r-poiln3"})
    bio = bioUnformated.getText()

    account = {}
    account["displayname"] = displayname
    account["bio"] = bio

    return account

class twitterScraper:
    def __init__(self,fingerprint,debugMode,nitter):
        self._geolocation=fingerprint.get("geolocation")
        self._locale=fingerprint.get("locale")
        self._permissions=fingerprint.get("permissions")
        self._storage_state=fingerprint.get("storage_state")
        self._timezone_id=fingerprint.get("timezone_id")
        self._user_agent=fingerprint.get("user_agent")

        self._debugMode = debugMode
        self._nitter = nitter

    def runScraper(self,playwright:Playwright,accountsList):
        browser = playwright.firefox.launch()
        context = browser.new_context(geolocation=self._geolocation, locale=self._locale, permissions=self._permissions, storage_state=self._storage_state, timezone_id=self._timezone_id, user_agent=self._user_agent)
        page = context.new_page()
        accountsMetadata = {}

        for acc in accountsList:
            print(f"scraping @{acc}")
            # looping over and over on page.goto, oxpecker crashed often having a timeout error
            while True:
                try:
                    page.goto(f"https://x.com/{acc}")
                    time.sleep(9)
                except playwrightTimeout:
                    print("Timeout error, going again")
                break
            # data of scraped account
            accountData = {}
            metadata = {}

            pfpUrl = getPfpUrl(acc,page,self._debugMode)
            metadata["pfp"] = pfpUrl
            loadMoreTweets(page)
            accHtml = page.content()

            if self._debugMode:
                with open(f".cache/test/indexOf{acc}.html","w") as firstIndex:
                    firstIndex.write(accHtml)

            originalTweets = self.scrape(accHtml,acc)
            with open(f".cache/scrape/{acc}-tweets.json","w") as scrapedFile:
                scrapedFile.write(json.dumps(originalTweets))

            # release ram
            accHtml = None
            originalTweets = None

            # switch to retweets
            page.get_by_role("tab", name="Reposts").click()
            loadMoreTweets(page)
            retweetAccHtml = page.content()

            if self._debugMode:
                with open(f".cache/test/indexOfRetweetsOf{acc}.html","w") as firstIndex:
                    firstIndex.write(retweetAccHtml)

            retweets = self.scrape(retweetAccHtml,acc)
            with open(f".cache/scrape/{acc}-retweets.json","w") as scrapedFile:
                scrapedFile.write(json.dumps(retweets))

            accountsMetadata[acc] = metadata

            # release ram
            metadata = None

        context.storage_state(path=self._storage_state) # saving new cookies in case website updates something

        context.close()
        browser.close()

        for acc in accountsList:
            print(f"Sorting @{acc} tweets")
            sortTweetsAndRetweets(acc,accountsMetadata[acc])
        accountsMetadata = {}

    def scrape(self,pageHtml,account):
        soup = BeautifulSoup(pageHtml,"html.parser")
        articlesHtml = soup.find_all('article')

        tweets = []

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
            refTweetText = articleSoup.find("div",{"data-testid":"tweetText","style":"-webkit-line-clamp: 5; color: rgb(15, 20, 25);"}) # div in which there is ref tweet text

            tweetText = articleSoup.find("div", {"data-testid":"tweetText"}) # normal tweet text
            if not refTweetText == tweetText:
                tweetList = []
                strTweetText = str(tweetText)
                tweetTextSoup = BeautifulSoup(strTweetText,"html.parser")
                for tag in tweetTextSoup.children:
                    emojiList = tag.findAll("img",{"class":"r-4qtqp9 r-dflpy8 r-k4bwe5 r-1kpi4qh r-pp5qcn r-h9hxbl"}) # twitter pusts emojis as imgs
                    for emojiLoop in emojiList:
                        emoji = emojiLoop["alt"]
                        tag.img.replace_with(emoji)
                    text = tag.getText()
                    formatedText = text.replace("@",f"{self._nitter}/")
                    tweetList.append(formatedText)
                tweetStr = "".join(tweetList)
            else:
                # if they are the same that means author did not write anything, only referenced some tweet
                tweetStr = None

            # reading tweet author
            tweetAuthorBar = articleSoup.find("div",{"class":"css-146c3p1 r-bcqeeo r-1ttztb7 r-qvutc0 r-37j5jr r-a023e6 r-rjixqe r-b88u0q r-1awozwy r-6koalj r-1udh08x r-3s2u2q"})
            strTweetAuthorBar = str(tweetAuthorBar)
            authorTweetSoup = BeautifulSoup(strTweetAuthorBar,"html.parser")
            authorTweet = authorTweetSoup.find("span",{"class":"css-1jxf684 r-bcqeeo r-1ttztb7 r-qvutc0 r-poiln3"})
            if authorTweet == None: # if there is no span with that class tweets is probably invalid
                continue
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
            reTweetAndPinnedBar = articleSoup.find("div",{"class":"css-g5y9jx"})
            strReTweetAndPinnedBar = str(reTweetAndPinnedBar)

            upperTweetBarSoup = BeautifulSoup(strReTweetAndPinnedBar,"html.parser")
            if upperTweetBarSoup.findAll("div",{"data-testid":"socialContext"}): # this div only exists for pinned tweets
                isPinned = True

            if upperTweetBarSoup.findAll("span",{"data-testid":"socialContext"}): # this span only exists in that div when tweet is reposted
                isRetweet = True

            # getting tweet url
            tweetMetadata = articleSoup.find("a",{"class":"css-146c3p1 r-bcqeeo r-1ttztb7 r-qvutc0 r-37j5jr r-a023e6 r-rjixqe r-16dba41 r-xoduu5 r-1q142lx r-1w6e6rj r-9aw3ui r-3s2u2q r-1loqt21"})
            try:
                tweetUrl = tweetMetadata["href"]
            except TypeError:
                tweetUrl = None

            # getting tweet post date
            tweetPostDate = articleSoup.find("time")
            tweetPostDateInDatetime = datetime.datetime.fromisoformat(tweetPostDate["datetime"])
            tweetPostDateInUnix = tweetPostDateInDatetime.timestamp()

            # checking if tweet is refering to another tweet
            hasRef = False
            refTweetAuthorUsername = None
            tweetRef = articleSoup.find("div",{"class":"css-g5y9jx r-adacv r-1udh08x r-1ets6dv r-1867qdf r-rs99b7 r-o7ynqc r-6416eg r-1ny4l3l r-1loqt21"})
            if tweetRef is not None:
                hasRef = True

                # reading refered tweet author username
                refTweetSoup = BeautifulSoup(str(tweetRef),"html.parser")
                refTweetUsernameDiv = refTweetSoup.find("div",{"class":"css-146c3p1 r-dnmrzs r-1udh08x r-1udbk01 r-3s2u2q r-bcqeeo r-1ttztb7 r-qvutc0 r-37j5jr r-a023e6 r-rjixqe r-16dba41 r-18u37iz r-1wvb978"})
                refTweetUsernameDivSoup = BeautifulSoup(str(refTweetUsernameDiv),"html.parser")
                refTweetUsernameSpan = refTweetUsernameDivSoup.find("span",{"class":"css-1jxf684 r-bcqeeo r-1ttztb7 r-qvutc0 r-poiln3"})
                refTweetAuthorUnformated = refTweetUsernameSpan.get_text()
                refTweetAuthorUsername = refTweetAuthorUnformated.replace("@",f"{self._nitter}/")

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
            tweet["refTweetAuthorUsername"] = refTweetAuthorUsername
            tweet["url"] = tweetUrl
            tweet["time"] = tweetPostDateInUnix
            tweet["id"] = tweetId

            tweets.append(tweet)

        return tweets





