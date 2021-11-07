import socket
from .connection import RawConnection


async def server():
    sock = socket.socket()#socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((socket.gethostname(), 933))
    sock.listen(2)
    while True:
        print("Accepting")
        conn, dynamic_port = sock.accept()
        conn = RawConnection(conn)
        await conn.send(b"Hello!")
        await conn.close()
    sock.close()
