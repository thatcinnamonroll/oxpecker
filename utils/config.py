import json
import os

oxpeckerDir = os.getcwd()

def ensureDataFiles():
    if not os.path.exists(f"{oxpeckerDir}/.data"):
        os.makedirs(f"{oxpeckerDir}/.data")
        with open(f"{oxpeckerDir}/utils/defaultSettings.json","r") as stockSettingsFile:
            stockSettingsDir = json.load(stockSettingsFile)
            stockSettings = json.dumps(stockSettingsDir)
        open(f"{oxpeckerDir}/.data/userFollowed.json","w").write("{}")
        open(f"{oxpeckerDir}/.data/userSettings.json","w").write(stockSettings)

def ensureCacheFiles():
    if not os.path.exists(f"{oxpeckerDir}/.cache"):
        os.makedirs(f"{oxpeckerDir}/.cache")
        os.makedirs(f"{oxpeckerDir}/.cache/media")
        open(f"{oxpeckerDir}/.cache/cache.json","w").write('{   "posted":[]    }')

class BotConfig:
    def __init__(self):
        self._keepConfigLoop = True

    def follow(self,account,mastodonToken):
        if mastodonToken == "":
            mastodonToken = False
        with open(".data/userFollowed.json","r") as followedFile:
            userFollowed = json.load(followedFile)
        userFollowed[account] = mastodonToken
        with open(".data/userFollowed.json","w") as followedFile:
            followedFileJson = json.dumps(userFollowed,indent=4)
            followedFile.write(followedFileJson)
        print(f"followed @{account}")

    def unFollow(self,account):
        with open(".data/userFollowed.json","r") as followedFile:
            userFollowed = json.load(followedFile)
        userFollowed.pop(account,None)
        with open(".data/userFollowed.json","w") as followedFile:
            followedFileJson = json.dumps(userFollowed,indent=4)
            followedFile.write(followedFileJson)
        print(f"unfollowed @{account}")

    def configList(self,userInput):
        if userInput == "followed":
            with open(".data/userFollowed.json","r") as followedFile:
                userFollowed = json.load(followedFile)
            print("Followed user ------ Mastodon Api Key")
            for user in userFollowed:
                print(f"@{user} ---- {userFollowed[user]}")
        elif userInput == "config":
            with open(".data/userSettings.json",'r') as settingsFile:
                settings = json.load(settingsFile)
            print("----- Configs -----")
            print(f"Nitter: {settings["nitter"]}")
            print(f"Mastodon: {settings["mastodon"]}")
            print(f"Wait time: {settings["waitTime"]}")
        else:
            print("No option with that name")
            print(": list followed -- lists followed accounts and api keys assigned to them")
            print(": list config -- lists all user configs")

    # def setup(self):

    def userChoiceParser(self,userInput):
        if userInput == "h" or userInput == "help":
            print("Oxpecker config tool helper")
            print("Commands ----")
            print(": follow <twitter-user> - add username typed here to userFollowed.json, making bot scrape its account")
            print(": unfollow <twitter-user> - remove from userFollowed.json ")
            print(": setup - initial setup -- work in progress")
            print(": exit - quit config mode")
            print(": list <what-to-list> - lists configs or followed")
            print(": clear-cache - deletes cache folder -- work in progress")
        elif userInput == "exit":
            self._keepConfigLoop = False
        elif userInput.startswith("follow"):
            splitedInput = userInput.split(" ")
            twitterAcc = splitedInput[1]
            print("Please enter mastodon token for that twitter page (if you dont want to post to mastodon press enter)")
            userToken = input(": ")
            self.follow(twitterAcc,userToken)
        elif userInput.startswith("unfollow"):
            splitedInput = userInput.split(" ")
            twitterAcc = splitedInput[1]
            self.unFollow(twitterAcc)
        elif userInput.startswith("list"):
            splitedInput = userInput.split(" ")
            try:    # list in python dont have safe func like .get() :\
                listOpt = splitedInput[1]
            except IndexError:
                listOpt = None
            self.configList(listOpt)

ensureCacheFiles()
ensureDataFiles()
