import socket
import asyncio
from sockbyte import ChunkedConnection


async def client():
    print("Opening connection")
    reader, writer = await asyncio.open_connection(socket.gethostname(), 933)
    conn = ChunkedConnection(reader, writer)
    print("Receiving")
    for i in range(2):
        while True:
            if message := await conn.receive():
                print(repr(message))
                break


