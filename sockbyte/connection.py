import time
from asyncio import StreamReader, StreamWriter
from sockbyte.exceptions import (
    SocketError,
    ContentTypeError
)


class RawConnection:
    HEADER_LENGTH = 8
    CHUNK_TIMEOUT_MS = 1000

    def __init__(self, reader: StreamReader, writer: StreamWriter) -> None:
        self.reader = reader
        self.writer = writer

    async def rawsend(self, data: bytes) -> None:
        header = self.header(data)
        self.writer.write(header)
        await self.writer.drain()
        self.writer.write(data)
        await self.writer.drain()

    def header(self, data: bytes) -> bytes:
        content_length = str(len(data)).encode()
        return b"0" * (self.HEADER_LENGTH - len(content_length)) + content_length

    def decode_header(self, data: bytes) -> int:
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
        
        start = time.time() * 1000
        while len(data) < content_length:
            if time.time() * 1000 - start > self.CHUNK_TIMEOUT_MS:
                raise TimeoutError()
            time.sleep(0.001)
            data += await self.reader.read(content_length-len(data))
        return data

    async def close(self) -> None:
        self.writer.close()
        await self.writer.wait_closed()


