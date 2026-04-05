import json
import os
from utils.configHelper import *

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
            print(f"Debug mode: {settings["debugMode"]}")
        else:
            print("No option with that name")
            print(": list followed -- lists followed accounts and api keys assigned to them")
            print(": list config -- lists all user configs")

    def setup(self):
        print("Warning if oxpecker is already set up running this command will clear all settings!")
        shallContinue = input("Do you want to continue? [y/N]: ")
        if not shallContinue == "y":
            return
        auth_token = {}
        print("Making all dirs and files")
        ensureCacheFiles()
        ensureDataFiles()
        makeTwitterCacheFile()
        # loging into twitter
        print("Done now please login to scrape account in browser, and search for 'auth_token' cookie")
        input("When you are ready press enter: ")
        auth_token["value"] = input("Please paste here 'value' line: ")
        auth_token["expires"] = input("Please paste here 'expires' line (in unix time): ")
        insertAuthTokenCookie(auth_token)
        # settings
        print("Okay now settings, we are gona set browser fingerprint for now")
        geolocation = input("Now please type latitude and longitude you want the browser to have in that format (<latitude>/<longitude>): ")
        separatedGeolocale = geolocation.split("/")
        locale = input("Now please type locale, for example (de-DE): ")
        timezoneId = input("Now please type timezone id, for example (Europe/Berlin): ")
        userAgent = input("Now please type user agent, if you want to get list of most used ones press enter: ")
        if userAgent == "":
            userAgent = getUserAgent()
        print("Browser fingerprint done, now oxpecker settings")
        nitter = input("Type here your preffered nitter instance (with the https://): ")
        mastodonUrl = input("Type here url of mastodon on which you host your bots: ")
        waitTime = input("Type here how long do you want oxpecker to wait before each scraping sessions (in seconds, if you want to scrape once press enter): ")
        if waitTime == "":
            waitTime = False
        else:
            waitTime = int(waitTime)
        setupSettingsFile(separatedGeolocale,locale,timezoneId,userAgent,nitter,mastodonUrl,waitTime)

    def debugmode(self,state):
        with open(".data/userSettings.json","r") as settingsFile:
            userSettings = json.load(settingsFile)
        userSettings["debugMode"] = state
        with open(".data/userSettings.json","w") as settingsFile:
            settingsJson = json.dumps(userSettings,indent=4)
            settingsFile.write(settingsJson)

    def userChoiceParser(self,userInput):
        if userInput == "h" or userInput == "help":
            print("Oxpecker config tool helper")
            print("Commands ----")
            print(": follow <twitter-user> - add username typed here to userFollowed.json, making bot scrape its account")
            print(": unfollow <twitter-user> - remove from userFollowed.json ")
            print(": setup - initial setup")
            print(": exit - quit config mode")
            print(": list <what-to-list> - lists configs or followed")
            print(": clear-cache - deletes cache folder -- work in progress")
            print(": debugmode <on/off> - enable or disable debug mode")
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
        elif userInput.startswith("setup"):
            self.setup()
        elif userInput.startswith("debugmode"):
            splitedInput = userInput.split(" ")
            state = splitedInput[1]
            if state == "on":
                state = True
                self.debugmode(state)
            elif state == "off":
                state = False
                self.debugmode(state)
            else:
                print("Sorry i did not get that, you shoud type <on> or <off>")

ensureCacheFiles()
ensureDataFiles()
