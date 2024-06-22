import asyncio
from icmplib import async_ping, NameLookupError
from skpy import Skype

async def is_alive(address):
    try:
        host = await async_ping(address, count=3)  # Ping each address 3 times
        return host.is_alive
    except NameLookupError as e:
        print(f"Name lookup error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

def send_skype_notification(down_addresses):
    skype_username = 'vidbot2025@outlook.com'
    skype_password = 'dhPzF3meW6$5u8NA'
    
    # Connect to Skype
    sk = Skype(skype_username, skype_password)

    # Replace with your group chat ID or individual contact ID
    group_chat_id = "19:03fb1a3c75384a6db49f4c02c4bf4414@thread.skype"

    # Retrieve or create the group chat
    try:
        group_chat = sk.chats[group_chat_id]
    except KeyError:
        print(f"Chat ID {group_chat_id} not found.")
        return

    # message = f"The following servers are down: {', '.join(down_addresses)}"
    group_chat.sendMsg(f"{''.join(down_addresses)}")

async def monitor_servers(addresses, interval):
    server_status = {address: True for address in addresses}  # Initialize all servers as up

    while True:
        for address in addresses:
            is_server_up = await is_alive(address)
            
            if is_server_up and not server_status[address]:
                send_skype_notification(f"Server {address} is up.")
                server_status[address] = True
            elif not is_server_up and server_status[address]:
                send_skype_notification(f"Server {address} is down.")
                server_status[address] = False

        await asyncio.sleep(interval)

if __name__ == "__main__":
    addresses = ['10.1.50.21', '127.0.0.1', '::1']
    interval = 3  # Time interval in seconds between checks
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(monitor_servers(addresses, interval))
