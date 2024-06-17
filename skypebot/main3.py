import os
import pandas as pd
from zipfile import ZipFile
import shutil
from pathlib import Path
from skpy import SkypeEventLoop, SkypeNewMessageEvent
import pyodbc
import paramiko
import re
from PIL import Image, ImageDraw, ImageFont
import stat
from dotenv import load_dotenv
import subprocess
import sys
import time
# -------------------------------------------------------------------
####
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# -------------------------------------------------------------------
#font_path = "/usr/share/fonts/truetype/Tahoma.ttf"
# Load environment variables from .env file
load_dotenv()

# Accessing environment variables
myLocalDBConn = os.getenv('LOCAL_DB_CONN')
sftp_host = os.getenv('SFTP_HOST')
sftp_port = os.getenv('SFTP_PORT')
sftp_user = os.getenv('SFTP_USER')
sftp_password = os.getenv('SFTP_PASSWORD')
skype_user = os.getenv('SKYPE_USER')
skype_password = os.getenv('SKYPE_PWD')

# Now you can use these variables in your script

#-----------------------------------------------------------------

class SkypeListener(SkypeEventLoop):
    """ Listen to a channel continuously """
    

    def __init__(self):

        super().__init__(skype_user, skype_password)
        self.stop_listening = False
        
        self.LOANEID_pattern = re.compile(r'((mir)|(vcr)|(ocr)|(atm)|(sen)|(mnc)|(dcr)|(mnv)|(shi)|(tkm))\d+')
        self.GetInfo_pattern = re.compile(r'^getinfo\s+((mir)|(vcr)|(ocr)|(atm)|(sen)|(mnc)|(dcr)|(mnv)|(shi)|(tkm))\d+\s*$')
                
        self.Group_ID = '19:03fb1a3c75384a6db49f4c02c4bf4414@thread.skype'
        self.Group = self.chats[self.Group_ID]

        # Combined regex patterns for both getinfo and getsms
        self.GetSms_pattern = re.compile(r'^(getinfo|getsms[123])\s+((mir)|(vcr)|(ocr)|(atm)|(sen)|(mnc)|(dcr)|(mnv)|(shi)|(tkm))\d+\s*$')
        self.SMStemplate_pattern = re.compile('^getsms[123]')



        self.SMS_font = ImageFont.truetype("Tahoma.ttf", 14)
        self.SMS_Wartermark_font = ImageFont.truetype("Tahoma.ttf", 34)

    def onEvent(self, event):

        if isinstance(event, SkypeNewMessageEvent):
            message = {"user_id": event.msg.userId,
                       "chat_id": event.msg.chatId,
                       "msg": event.msg.content}
            #print(message["chat_id"])
            if message["chat_id"] == self.Group_ID:
            #if message["chat_id"] == "abc":
            
                if self.GetInfo_pattern.match(message["msg"].lower()) != None:

                    SearchValue = self.LOANEID_pattern.search(message["msg"].lower()).group()
                    if SearchValue != None:
                        my_db_conn = pyodbc.connect(myLocalDBConn)

                        self.Group.sendMsg(
                            '@{}: Yeu cau dang duoc xy lu'.format(message["user_id"]))
                        print("@{}: Yeu cau dang duoc xy lu")


                        result = pd.read_sql_query("""
                                EXEC [localDB].[dbo].[SkypeGetInfo]
                                @userName = '{}'
                                ,@Domain = '{}'
                                ,@SearchKey = {}
                                ,@SearchValue = '{}'
                            """.format(message["user_id"], 'Inhouse', 1, SearchValue)
                        , my_db_conn)

                        my_db_conn.commit()
                        my_db_conn.close()

                        rowCount = result['ID'].count()

                        if rowCount == 0:
                            # print('Status: "{}" not found'.format(SearchValue))
                            self.Group.sendMsg('@{}: Khong tim thay hop dong "{}"'.format(message["user_id"], SearchValue))
                            print('@{}" ": Khong tim thay hop dong "{}"')                    
                        else:
                            # print('Path: {}'.format(result["Path"][0]))

                            destinationPath = os.path.join(r"Output", SearchValue)

                            if os.path.exists(destinationPath):
                                shutil.rmtree(destinationPath)

                            Path(destinationPath).mkdir(
                                parents=True
                                # ,exist_ok=True
                            )

                            ssh.connect(sftp_host, sftp_port, sftp_user, sftp_password)
                            sftp = ssh.open_sftp()

                            #             # shutil.copy(sourcePath, destinationPath)
                            for path in result["Path"]:
                                temp = sftp.lstat(path)
                                if stat.S_ISDIR(temp.st_mode):
                                    for file in sftp.listdir(path):
                                        # shutil.copy(os.path.join(result["Path"], file), destinationPath)
                                        fullSourcePath = path + '/' + file
                                        fullDestPath = destinationPath + '\\' + file
                                        sftp.get(fullSourcePath, fullDestPath)
                                        print(fullSourcePath, '-', fullDestPath)
                                else:
                                    fullSourcePath = path
                                    fullDestPath = destinationPath + '\\' + os.path.basename(path)
                                    sftp.get(fullSourcePath, fullDestPath)
                                    print(fullSourcePath, '-', fullDestPath)

                            ssh.close

                            with ZipFile(os.path.join(r".\Output", SearchValue + '.zip'), 'w') as zipObj:
                                for folderName, subfolders, filenames in os.walk(destinationPath):
                                    for filename in filenames:
                                        # create complete filepath of file in directory
                                        filePath = os.path.join(folderName, filename)
                                        # Add file to zip
                                        zipObj.write(filePath, os.path.basename(filePath))

                            zipObj.close()

                            fullPath = os.path.join(r".\Output", SearchValue + '.zip')
                            fileName = os.path.basename(fullPath)

                            try:
                                sent2User = self.contacts[message["user_id"]].chat
                                sent2User.sendFile(open(fullPath, "rb"), fileName, image=False)  # file upload
                                self.Group.sendMsg('@{}: Hop dong "{}" da duoc gui cho ban'.format(message["user_id"], SearchValue))
                                print('@{}: Hop dong "{}" da duoc gui cho ban')

                            except ValueError:
                                print("Oops! Check your contacts & try again...")

    
                elif self.GetSms_pattern.match(message["msg"].lower()) != None:
                    SearchValue = self.LOANEID_pattern.search(message["msg"].lower()).group()
                    Template = self.SMStemplate_pattern.search(message["msg"].lower()).group()[-1]
                    if SearchValue != None:
                        self.Group.sendMsg(
                            '@{}: Yeu cau dang duoc xu ly'.format(message["user_id"]))
                        print("@{}: Yeu cau dang duoc xu ly")

                        my_db_conn = pyodbc.connect(myLocalDBConn)
                        result = pd.read_sql_query("""
                            EXEC [localDB].[dbo].[SkypeGetSMS]
                                @SkypeId = '{}'
                                ,@SkypeGroup = '{}'
                                ,@SearchValue = '{}'
                                ,@Template = {}
                            """.format(message["user_id"], message["chat_id"], SearchValue, Template)
                                                       , my_db_conn)

                        my_db_conn.commit()
                        my_db_conn.close()

                        rowCount = result['Active'].count()
                        if rowCount == 0:
                            self.Group.sendMsg(
                                'Khong tim thay hop dong "{}"/ Ban chua co quyen su dung tinh nang nay'.format(SearchValue))
                            print('Khong tim thay hop dong "{}"/ Ban chua co quyen su dung tinh nang nay')
                        else:
                            if result['UserPermission'][0] == 0:
                                self.Group.sendMsg(
                                    'Khong tim thay hop dong "{}"/ Ban chua co quyen su dung tinh nang nay'.format(SearchValue))
                                print('Khong tim thay hop dong "{}"/ Ban chua co quyen su dung tinh nang nay')
                            elif result['Active'][0] == 0:
                                self.Group.sendMsg(
                                    'Hop dong da tat toan')
                                print("Hop dong da duoc tat toan")
                            # elif result['AssignedTo'][0] != 'Inhouse':
                            # elif result['AssignedTo'][0] != 'Inhouse' and result['AssignedTo'][0] != 'ManualCallJune' and result['AssignedTo'][0] != 'ManualCallJuly':
                            elif ('Inhouse' not in result['AssignedTo'][0] \
                                    and 'Manual' not in result['AssignedTo'][0] \
                                    and 'notAssign' not in result['AssignedTo'][0] \
                                    and 'Waive' not in result['AssignedTo'][0]\
                                    and result['AssignedTo'][0] != 'AiRudder' \
                                    and result['AssignedTo'][0] != 'MFI Potential' \
                                    and result['AssignedTo'][0] != 'Legal Collection'\
                                    and result['AssignedTo'][0] != 'MFI Skip Work' \
                                    and result['AssignedTo'][0] != 'Bank Skip Work' \
                                    and result['AssignedTo'][0] != 'Bank Facebook'\
                                    and result['AssignedTo'][0] != 'Bank Zalo' \
                                    and result['AssignedTo'][0] != 'Additional_Bank'\
                                    and result['AssignedTo'][0] != 'Additional_MFI' \
                                    and result['AssignedTo'][0] != 'MFI Facebook' \
                                    and result['AssignedTo'][0] != 'Low balance' \
                                    and result['AssignedTo'][0] != 'Low_Balance1' \
                                    and 'RBC' not in result['AssignedTo'][0]\
                                    ):
                                self.Group.sendMsg(
                                    'Hop dong nay hien tai khong duoc phan cong cho Inhouse')
                                print("Hop dong nay hien tai khong duoc phan cong cho Inhouse")
                            else:

                                if Template == '1':
                                    SMS_img = Image.new('RGB', (500, 450))
                                elif Template == '2':
                                    SMS_img = Image.new('RGB', (500, 265))
                                elif Template == '3':
                                    SMS_img = Image.new('RGB', (500, 440))
                                else:
                                    SMS_img = Image.new('RGB', (500, 800))

                                SMS_draw = ImageDraw.Draw(SMS_img)

                                SMS_Wartermark = result['CrmUser'][0]
                                SMS_draw.text((20, 50), SMS_Wartermark, font=self.SMS_Wartermark_font,
                                                fill=(0, 65, 0, 30))
                                SMS_draw.text((20, 160), SMS_Wartermark, font=self.SMS_Wartermark_font,
                                                fill=(0, 65, 0, 30))
                                SMS_draw.text((20, 350), SMS_Wartermark, font=self.SMS_Wartermark_font,
                                                fill=(65, 0, 0, 30))

                                SMS_text = result['SMS'][0].replace('\r\n', '\n')
                                # print(SMS_text)
                                SMS_draw.text((10, 20), SMS_text, font=self.SMS_font)
                                # SMS_img = SMS_img.rotate(270, expand=True)

                                fullPath = os.path.join(r".\Output", SearchValue + '_SMS' + Template + '.jpg')
                                fileName = os.path.basename(fullPath)

                                SMS_img.save(fullPath)

                                try:
                                    sent2User = self.contacts[message["user_id"]].chat

                                    sent2User.sendFile(open(fullPath, "rb"), fileName, image=True)  # file upload


                                except ValueError:
                                    print("Oops! Check your contacts & try again...")

                                self.Group.sendMsg(
                                    'Tin nhan mau da duoc gui cho ban')
                                print("Tin nhan mau da duoc gui cho ban")


# ----START OF SCRIPT
if __name__ == "__main__":
    SkypeGetInfo = SkypeListener()
    print("I'm Lisenting")
    SkypeGetInfo.loop()
