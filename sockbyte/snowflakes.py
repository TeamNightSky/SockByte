import random
import time
import hashlib


def packet_snowflake(packet) -> bytes:
    data = packet.data + \
        str(time.time()).encode() + \
        str(random.randint(0, 999999)).encode()
    return hashlib.sha1(data).hexdigest().encode()

