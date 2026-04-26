from utils.mastodon import mastodonBot
import json
import requests

def downloadImg(url):
    imgRequest = requests.get(url)
    # getting img id
    urlSeperated = url.split("https://pbs.twimg.com/media/")
    imgId = urlSeperated[1]
    open(f".cache/media/{imgId}.jpg","wb").write(imgRequest.content)
    return imgId

class Bot:
    def __init__(self,nitter,mastodon,cache,followed,waitTime):
        self._nitterInstance = nitter
        self._mastodon = mastodon
        self._cache = cache
        self._postedTweets = cache["posted"]
        self._followed = followed
        self._waitTime = waitTime

    def readAndPost(self,scrapedDataTwitter):
        # reading everything and posting to mastodon
        for followed in scrapedDataTwitter:
            print(f"reading tweets from @{followed}")
            botApiKey = self._followed[followed]
            postedTweetsCount = 0 # counting posted tweets
            # mainly for debugging, if some api key will be set to false it wont be posted on mastodon
            if botApiKey == False:
                print(f"Skipped @{followed}, mastodon token set to false")
                continue
            tweets = scrapedDataTwitter[followed]
            tweets.reverse() # otherwise it posts tweets in the reverse order
            for tweet in tweets:
                tweetStrList = []
                mediaList = None
                if tweet["id"] in self._postedTweets:
                    continue
                if tweet["isPinned"]:
                    continue
                if tweet["isRetweet"]:
                    tweetStrList.append(f"[This is retweet from {self._nitterInstance}/{tweet["authorUsername"]}]")
                if tweet["hasVideo"]:
                    tweetStrList.append("[This tweet has video]")
                if tweet["hasRef"]:
                    tweetStrList.append("[This tweet is refering to other tweet]")
                if not tweet["media"] == []:
                    mediaList = []
                    for mediaUrl in tweet["media"]:
                        mediaId = downloadImg(mediaUrl)
                        mediaOpen = open(f".cache/media/{mediaId}.jpg",'rb')
                        mediaList.append(mediaOpen)
                tweetStrList.append(f" {tweet["text"]}")
                tweetStrList.append(f"\n [Nitter URL: {self._nitterInstance}{tweet["url"]} ]")
                tweetStr = "".join(tweetStrList)
                mastodonBot(botApiKey,self._mastodon).post(tweetStr,mediaList)
                self._postedTweets.append(tweet["id"])
                postedTweetsCount += 1
            print(f"Posted {postedTweetsCount} tweets from @{followed} to mastodon")
        with open(".cache/cache.json","w") as cacheFile:
            self._cache["posted"] = self._postedTweets
            cacheJson = json.dumps(self._cache,indent=4)
            cacheFile.write(cacheJson)

