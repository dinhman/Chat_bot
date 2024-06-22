# from icmplib import ping

# hosts = input("Nhap hosts")

# check = ping(hosts, count=10, interval=0.2)

# print(f"{check}")


import asyncio
from icmplib import async_ping
# async def is_alive(address):
#     host = await async_ping(address, count=10, interval=0.2)
#     return host.is_alive

# asyncio.run(is_alive('1.1.1.1'))

# True

async_ping('1.1.1.1', count=4, interval=1, timeout=2, id=None, source=None, family=None, privileged=True)