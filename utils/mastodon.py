import requests
import time
import secrets
import json

def makeMastodonAccount(username,accountSettings,botUrl,botToken):
    shouldAskForPassword = accountSettings["userManagesPasswords"]
    email = f"{username}{accountSettings["emailPrefix"]}"
    locale = accountSettings["locale"]
    if shouldAskForPassword:
        password = input(f"Type password for bot account posting from twitter profile @{username}: ")
    else:
        password = secrets.token_urlsafe(40)

    header = {'Authorization': f'Bearer {botToken}','content-type':'application/json'}

    data = {
        "reason":f"Submitted by oxpecker bot this account will be used to repost stuff from twitter account @{username}",
        "username":username,
        "email":email,
        "password":password,
        "agreement":True,
        "locale":locale
        }

    requestData = json.dumps(data).encode("utf-8")

    response = requests.post(f"{botUrl}/api/v1/accounts",data=requestData,headers=header)
    time.sleep(1) # wait for the request

    if response.status_code == 200:
        responseData = response.json()
        botToken = responseData["access_token"]
        print(f"Bot account for @{username} was successfully subbmited")
        return botToken
    else:
        print(f"Something went wrong, Error code: {response.status_code}")
        return None

class mastodonBot:
    def __init__(self,botToken,botUrl,debugmode=False):
        self.botToken = botToken
        self.botUrl = botUrl
        self.debugmode = debugmode

        # media in post func means list/array with open("path/to/file",'rb')
    def post(self,newPost,media=None):
        requestData = {'status':newPost}
        if media is not None:
            mediaList = []
            for mediaFile in media:
                mediaId = self.sendMedia(mediaFile)
                mediaList.append(mediaId)
            requestData['media_ids[]'] = mediaList
        requestHeader = {'Authorization': f'Bearer {self.botToken}'}
        response = requests.post(f"{self.botUrl}/api/v1/statuses",data=requestData,headers=requestHeader)
        time.sleep(2) # to avoid race condition
        if self.debugmode:
            if response.status_code == 200:
                print("Posted!")
            else:
                print(f"Something went wrong, Error code: {response.status_code}")
                print(response.content)


    def sendMedia(self,media):
        requestHeader = {'Authorization': f'Bearer {self.botToken}'}
        requestMedia = {'file':media}
        request = requests.post(f"{self.botUrl}/api/v1/media",files = requestMedia,headers=requestHeader)
        response = request.json()
        if request.status_code == 200 or request.status_code == 202:
            imgId = str(response.get("id"))
        else:
            imgId = None
        return imgId
        if self.debugmode:
            if response.status_code == 200:
                print("Img send")
            else:
                print(f"Something went wrong, Error code: {response.status_code}")
                print(response.content)

    def updatePfp(self,pfp):
        requestHeader = {'Authorization': f'Bearer {self.botToken}'}
        requestMedia = {'avatar':pfp}
        request = requests.patch(f"{self.botUrl}/api/v1/accounts/update_credentials",files=requestMedia,headers=requestHeader)

    def updateAccountInfo(self,accountInfo,accountSettings,nitter,username):
        discovarable = accountSettings["discovarable"]
        botAccount = accountSettings["botAccount"]
        locked = accountSettings["locked"]
        enableRss = accountSettings["enable_rss"]
        hideCollectionFollowers = accountSettings["hide_collections_followers"]
        webVisibility = accountSettings["web_visibility"]
        displayname = accountInfo["displayname"]
        bio = accountInfo["bio"]

        requestHeader = {'Authorization': f'Bearer {self.botToken}','content-type':'application/json'}

        data = {
            "discoverable":discovarable,
            "bot":botAccount,
            "display_name":displayname,
            "note":bio,
            "locked":locked,
            "enable_rss":enableRss,
            "hide_collections":hideCollectionFollowers,
            "web_visibility":webVisibility,
            "fields_attributes[0][name]":"Official Profile",
            "fields_attributes[0][value]":f"{nitter}/{username}"
        }

        requestData = json.dumps(data).encode("utf-8")

        response = requests.patch(f"{self.botUrl}/api/v1/accounts/update_credentials",data=requestData,headers=requestHeader)
        time.sleep(2) # wait for request

        if response.status_code == 200:
            responseData = response.json()
            print(f"Bot account for @{username} was successfully updated")
        else:
            print(f"Something went wrong, Error code: {response.status_code}")
