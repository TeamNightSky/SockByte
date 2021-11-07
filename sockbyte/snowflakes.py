import random
import time
import hashlib


def packet_snowflake(packet) -> str:
    data = packet.data + \
        str(time.time()).encode() + \
        str(random.randint(0, 999999)).encode()
    return hashlib.sha256(data).hexdigest()

