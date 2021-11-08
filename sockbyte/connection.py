import socket
from asyncio import StreamReader, StreamWriter
from sockbyte.exceptions import (
    SocketError,
    ContentTypeError
)
from sockbyte.message import (
    RawMessage,
    Chunk,
    ChunkReception
)


class RawConnection:
    HEADER_LENGTH = 32

    def __init__(self, reader: StreamReader, writer: StreamWriter) -> None:
        self.reader = reader
        self.writer = writer

    async def rawsend(self, data: bytes) -> None:
        header = self.header(data)
        self.writer.write(header)
        self.writer.write(data)
        await self.writer.drain()

    def header(self, data: bytes):
        content_length = str(len(data)).encode()
        return b"0" * (self.HEADER_LENGTH - len(content_length)) + content_length

    def decode_header(self, data: bytes):
        try:
            return int(data)
        except ValueError:
            raise ContentTypeError("content length header was non-integer")

    async def rawreceive(self) -> bytes:
        content_length = await self.reader.read(self.HEADER_LENGTH)
        if content_length == b"":
            raise SocketError("Connection broken while receiving buffer")
        content_length = self.decode_header(content_length)
        data = await self.reader.read(content_length)
        if len(data) != content_length:
            raise SocketError("Connection broken while receiving data")
        return data

    async def close(self) -> None:
        self.writer.close()


class ChunkedConnection(RawConnection):
    chunkreception: ChunkReception

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chunkreception = ChunkReception()

    async def send(self, data: bytes, *args, **kwargs):
        packet = RawMessage(data, *args, **kwargs)
        for i, chunk in enumerate(packet.chunks()):
            await self.rawsend(chunk.bytes())

    async def receive(self):
        data = await self.rawreceive()
        chunk = Chunk.from_bytes(data)
        self.chunkreception.feed(chunk)
        return self.chunkreception.fetch()


