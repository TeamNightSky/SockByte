from ..message import (
    RawMessage,
    Chunk,
    ChunkReception
)
from ..connection import (
    RawConnection
)

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
