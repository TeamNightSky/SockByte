import socket
import asyncio
from .connections import ChunkedConnection


async def handle_client(reader, writer):
    print("Handling connection")
    conn = ChunkedConnection(reader, writer)
    await conn.send(b"Hello!" * 1024)
    await conn.send(b"[CLOSE]")


async def server():
    print("Starting server")
    
    server = await asyncio.start_server(
        handle_client,
        socket.gethostname(),
        933
    )
    print("Running server")
    async with server:
        await server.serve_forever()

