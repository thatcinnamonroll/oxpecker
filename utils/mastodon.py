import requests

class mastodonBot:
    def __init__(self,botToken,botUrl):
        self.botToken = botToken
        self.botUrl = f"https://{botUrl}"

    def post(self,newPost):
        requestData = {'status':newPost}
        requestHeader = {'Authorization': f'Bearer {self.botToken}'}
        requests.post(f"{self.botUrl}/api/v1/statuses",data=requestData,headers=requestHeader)