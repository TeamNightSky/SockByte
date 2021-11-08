from dataclasses import dataclass, field
import typing as t

from .snowflakes import packet_snowflake
from .exceptions import MalformedChunkError


@dataclass()
class Chunk:
    index: bytes
    total: bytes
    chunk_data: bytes
    message_id: bytes

    def bytes(self) -> bytes:
        return b"\n".join([
            self.index,
            self.total,
            self.chunk_data,
            self.message_id
        ])

    @staticmethod
    def from_bytes(data: bytes):
        try:
            fields = data.split(b"\n")
        except ValueError:
            raise MalformedChunkError
        try:
            return Chunk(*fields)
        except TypeError:
            raise MalformedChunkError(fields)



@dataclass(repr=False)
class RawMessage:
    data: bytes
    length: int = None
    chunk_size: int = 1024
    snowflake: bytes = None
    message_constructor: t.Callable = field(default=None, repr=False)
    snowflake_constructor: t.Callable = field(default=None, repr=False)

    def __post_init__(self) -> None:
        snowflake_constructor = self.snowflake_constructor
        if snowflake_constructor is None:
            snowflake_constructor = packet_snowflake
        self.snowflake = snowflake_constructor(self)
        self.length = len(self.data)

    def chunks(self) -> t.Generator[Chunk, None, None]:
        for i in range(self.chunk_count):
            chunk_data = self.data[i * self.chunk_size: (i + 1) * self.chunk_size]
            yield Chunk(
                str(i + 1).encode(),
                str(self.chunk_count).encode(),
                chunk_data,
                self.snowflake
            )

    @property
    def chunk_count(self) -> int:
        return len(self.data) // self.chunk_size + 1

    @staticmethod
    def from_chunks(snowflake: bytes, chunks: t.List[Chunk]):
        message_constructor = RawMessage.message_constructor
        if message_constructor is None:
            message_constructor = RawMessage
        chunks = sorted(chunks, key=lambda chunk: chunk.index)
        data = b"".join([chunk.chunk_data for chunk in chunks]) 
        return message_constructor(data, snowflake=snowflake)

    REPR_LENGTH = 50

    def __repr__(self) -> str:
        content = f"<RawMessage length={self.length!r} chunk_size={self.chunk_size!r} data={self.data!r} snowflake={self.snowflake!r}>"
        if len(content) > self.REPR_LENGTH:
            content = content[:self.REPR_LENGTH]
        return content + "...>"


class ChunkReception(dict):
    def feed(self, chunk: Chunk) -> None:
        if chunk.message_id not in self:
            self[chunk.message_id]["total"] = chunk.total
        self[chunk.message_id]["chunks"].append(chunk)

    def fetch(self) -> RawMessage:
        """The chunk candidates are running for chunk president."""
        for key, chunk_candidate in list(self.items()):
            if len(chunk_candidate["chunks"]) == int(chunk_candidate["total"]):
                message = RawMessage.from_chunks(key, chunk_candidate["chunks"])
                del self[key]
                return message

    def __missing__(self, key: bytes) -> dict:
        self[key] = {"total": None, "chunks": [], "completed": False}
        return self[key]
