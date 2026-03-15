from utils.mastodon import mastodonBot
import json

class Bot:
    def __init__(self,nitter,mastodon,cache,followed):
        self._nitterInstance = nitter
        self._mastodon = mastodon
        self._cache = cache
        self._postedTweets = cache["posted"]
        self._followed = followed

    def ReadAndPost(self,scrapedDataTwitter):
        # reading everything and posting to mastodon
        for followed in scrapedDataTwitter:
            print(f"reading tweets from @{followed}")
            botApiKey = self._followed[followed]
            postedTweetsCount = 0 # counting posted tweets
            # mainly for debugging, if some api key will be set to false it wont be posted on mastodon
            if botApiKey == False:
                continue
            tweets = scrapedDataTwitter[followed]
            for tweet in tweets:
                tweetStrList = []
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
                tweetStrList.append(f" {tweet["text"]}")
                tweetStrList.append(f"\n [Nitter URL: {self._nitterInstance}{tweet["url"]} ]")
                tweetStr = "".join(tweetStrList)
                mastodonBot(botApiKey,self._mastodon).post(tweetStr)
                self._postedTweets.append(tweet["id"])
                postedTweetsCount += 1
        with open(".cache/cache.json","w") as cacheFile:
            self._cache["posted"] = self._postedTweets
            cacheJson = json.dumps(self._cache,indent=4)
            cacheFile.write(cacheJson)
        print(f"Posted {postedTweetsCount} tweets from @{followed} to mastodon")
