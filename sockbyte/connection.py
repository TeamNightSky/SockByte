import socket
from sockbyte.exceptions import (
    SocketError,
    ContentTypeError
)
from sockbyte.message import RawMessage


class RawConnection:
    HEADER_LENGTH = 32

    def __init__(self, conn: socket.socket) -> None:
        self.conn = conn

    async def send(self, data: bytes) -> None:
        header = self.header(data)
        if self.conn.send(header) == 0:
            raise SocketError("Connection broken while sending buffer")
        if self.conn.send(data) == 0:
            raise SocketError("Connection broken while sending data")

    def header(self, data: bytes):
        content_length = str(len(data)).encode()
        return b"0" * (self.HEADER_LENGTH - len(content_length)) + content_length

    def decode_header(self, data: bytes):
        try:
            return int(data)
        except ValueError:
            raise ContentTypeError("content length header was non-integer")

    async def receive(self) -> bytes:
        content_length = self.conn.recv(self.HEADER_LENGTH)
        if content_length == b"":
            raise SocketError("Connection broken while receiving buffer")
        content_length = self.decode_header(content_length)

        data = self.conn.recv(content_length)
        if len(data) != content_length:
            raise SocketError("Connection broken while receiving data")
        return data

    async def close(self) -> None:
        self.conn.close()


class ChunkedConnection(RawConnection):
    async def send(self, data: bytes, *args, **kwargs):
        packet = RawMessage(data, *args, **kwargs)
        for chunk, i in enumerate(packet.chunks()):
            await super().send(chunk.bytes())

    def receive(self):
        pass

