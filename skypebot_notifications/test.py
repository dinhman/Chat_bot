from skpy import Skype, SkypeApiException
from pythonping import ping


try:
    # Replace with your actual Skype credentials
    username = 'vidbot2025@outlook.com'
    password = 'dhPzF3meW6$5u8NA'

    # Connect to Skype
    sk = Skype(username, password)

    # Replace with the Skype username or ID of the user you want to message
    user_id = "live:.cid.cf69b44f1c253509"
    group_id ="19:03fb1a3c75384a6db49f4c02c4bf4414@thread.skype"

    # Retrieve the SkypeUser object corresponding to user_id
    contact = sk.contacts[user_id]
    
    try:
        group = sk.chats[group_id]
    except KeyError:
        group = sk.chats.create([group_id])
    group.sendMsg("Hello world!")


    # Check if contact is valid
    # if contact:
    #     # Send a message to the user
    #     contact.chat.sendMsg('Hello, this is a direct message!')
    # else:
    #     print(f'Error: Contact {user_id} not found in your Skype contacts.')

except SkypeApiException as e:
    print(f'Error occurred: {e}')
except Exception as ex:
    print(f'Unexpected error occurred: {ex}')
