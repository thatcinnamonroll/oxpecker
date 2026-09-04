import json
import os
from utils.configHelper import *
from utils.mastodon import *

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
        os.makedirs(f"{oxpeckerDir}/.cache/pfp")
        os.makedirs(f"{oxpeckerDir}/.cache/test")
        open(f"{oxpeckerDir}/.cache/cache.json","w").write('{   "posted":[],    "pfp":{}    }')

class BotConfig:
    def __init__(self):
        self._keepConfigLoop = True
        self._sysExitAfterLoop = True

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
        print("All folders and files made, now please visit docs below for later instructions on setup")
        print("Docs url: COMMIG SOON")

    def changeSetting(self,settingName,settingVal):
        with open(".data/userSettings.json","r") as settingsFile:
            userSettings = json.load(settingsFile)
        userSettings[settingName] = settingVal
        with open(".data/userSettings.json","w") as settingsFile:
            settingsJson = json.dumps(userSettings,indent=4)
            settingsFile.write(settingsJson)

    def userChoiceParser(self,userInput):
        splitedInput = userInput.split(" ")
        if userInput == "h" or userInput == "help":
            print("Oxpecker config tool helper")
            print("Commands ----")
            print(": follow <twitter-user> - add username typed here to userFollowed.json, making bot scrape its account")
            print(": setup - initial setup")
            print(": exit - quit config mode and close oxpecker")
            print(": start - quit config mode and start oxpecker")
            print(": post-status - make a post on status account (if you have one)")
        elif userInput == "exit":
            self._keepConfigLoop = False
        elif userInput == "start":
            self._sysExitAfterLoop = False
            self._keepConfigLoop = False
        elif userInput.startswith("follow"):
            twitterAcc = splitedInput[1]
            twitterAccLowercase = twitterAcc.lower() # gotosocial does not accept uppercase usernames
            addFooter = True
            with open(".data/userSettings.json",'r') as fingerPrintFile:
                userSettings = json.load(fingerPrintFile)
                mastodonAccountSettings = userSettings["mastodonBotsSettings"]
                mastodonUrl = userSettings["mastodon"]
                token = userSettings["manageAccountToken"]
                browerFingerprint = userSettings["fingerprint"]
                nitter = userSettings["nitter"]
                debugmode = userSettings["debugMode"]
            botToken = makeMastodonAccount(twitterAccLowercase,mastodonAccountSettings,mastodonUrl,token)
            print("Please paste this command in your gotosocial container in order to accept bot account")
            print(f"./gotosocial admin account confirm --username {twitterAccLowercase}")
            input("When you are done press enter")
            # i've wasted whole WEEK thinking about it, reading Oauth docs etc. pls gotosocial devs fix accepting accounts
            # without the need to restart container :D
            print("Now please restart gotosocial container")
            input("When you are done press enter")
            print(f"Reading basic info about @{twitterAcc}")
            twitterAccInfo = getInfoAboutTwitterUser(twitterAcc,browerFingerprint,addFooter)
            print("Sending this info to bot account")
            mastodonBot(botToken,mastodonUrl,debugmode).updateAccountInfo(twitterAccInfo,mastodonAccountSettings,nitter,twitterAcc)
            with open(".data/userFollowed.json","r") as followedFile:
                userFollowed = json.load(followedFile)
                userFollowed[twitterAcc] = botToken
            with open(".data/userFollowed.json","w") as followedFile:
                followedFileJson = json.dumps(userFollowed,indent=4)
                followedFile.write(followedFileJson)
            print(f"followed @{twitterAcc}")
        elif userInput.startswith("setup"):
            self.setup()
        elif userInput == "post-status":
            postStatus()

ensureCacheFiles()
ensureDataFiles()
