import socket
import re
from .connection import RawConnection


async def client():
    sock = socket.socket()#socket.AF_INET, socket.SOCK_DGRAM)
    print("Conncecting")
    sock.connect((socket.gethostname(), 933))
    sock = RawConnection(sock)
    info_regex = "^\[(\w+)\:(\w+)\] (.*)"
    await sock.send(b"HI")

    while True:
        data = await sock.receive()
        data = data.decode('utf-8')
        try:
            info = re.findall(info_regex, data)
        except re.error as e:
            print(f"Regex error {e} while parsing packet {data} with pattern {info_regex}")
            continue
        if info:
            origin, info_type, message = info[0]
            print(message)
            if message == "Close":
                sock.conn.close()
                # Call some socket post_close event?
                break
        else:
            print(data)
