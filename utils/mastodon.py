import requests
import time

class mastodonBot:
    def __init__(self,botToken,botUrl):
        self.botToken = botToken
        self.botUrl = botUrl

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
        requests.post(f"{self.botUrl}/api/v1/statuses",data=requestData,headers=requestHeader)
        time.sleep(2) # to avoid race condition

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
