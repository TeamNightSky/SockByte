import socket
import asyncio
from .connection import ChunkedConnection


async def client():
    print("Opening connection")
    reader, writer = await asyncio.open_connection(socket.gethostname(), 933)
    conn = ChunkedConnection(reader, writer)
    print("Receiving")
    message = await conn.receive()
    print(message)
    message = await conn.receive()
    print(message)
    await conn.close()

