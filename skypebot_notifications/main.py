from skpy import Skype
import os
from dotenv import load_dotenv
from skpy import SkypeEventLoop, SkypeNewMessageEvent
from icmplib import ping


load_dotenv()

username_skp=os.getenv('SKYPE_USER')
password_skp=os.getenv('SKYPE_PWD')

hosts_to_ping = ['192.168.1.1', 'google.com', '8.8.8.8']  

# sk.chats
# sk=Skype(username, password) #connect to Skype
# sk.user
# sk.contacts

class SkypeListener(SkypeEventLoop):
    "Listen to a channel continuously"
    def __init__(self):
        super(SkypeListener, self).__init__(username_skp, password_skp)
        
        # self.userId = 'live:.cid.cf69b44f1c253509' #User ID
        self.groupId = '19:03fb1a3c75384a6db49f4c02c4bf4414@thread.skype' #chat ID
        

    def onEvent(self, event):
        print("onEvent called with event:", event)  # Debug statement
        if isinstance(event, SkypeNewMessageEvent):
            if event.msg.chatId == self.groupId and event.msg.content == "ping all":


            # default = "Skype listener: Investigate if you see this."
            # message = {"user_id":event.msg.userId,
            #            "chat_id":event.msg.chatId,
            #            "msg":event.msg.content}
            
            # if event.msg.chatId == self.groupId and event.msg.content == "ping":
                event.msg.chat.sendMsg("pong")


if __name__ == "__main__":
    my_skype = SkypeListener()
    my_skype.loop()

