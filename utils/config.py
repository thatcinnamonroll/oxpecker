import json

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

    def userChoiceParser(self,userInput):
        if userInput == "h" or userInput == "help":
            print("Oxpecker config tool helper")
            print("Commands ----")
            print(": follow <twitter-user> - add username typed here to userFollowed.json, making bot scrape its account")
            print(": unfollow <twitter-user> - remove from userFollowed.json ")
            print(": setup - initial setup -- work in progress")
            print(": exit - quit config mode")
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

