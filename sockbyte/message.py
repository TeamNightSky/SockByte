from dataclasses import dataclass
import typing as t

from .snowflakes import packet_snowflake
from .exceptions import MalformedChunkError


@dataclass()
class Chunk:
    index: bytes
    total: bytes
    chunk_data: bytes
    message_id: bytes

    def bytes(self):
        return b"\n".join([
            self.index,
            self.total,
            self.message_id,
            self.chunk_data
        ])

    @staticmethod
    def from_bytes(data: bytes):
        try:
            index, total, chunk_data, message_id = data.split(b"\n")
        except ValueError:
            raise MalformedChunkError
        return Chunk(index, total, chunk_data, message_id)


@dataclass()
class RawMessage:
    data: bytes
    chunk_size: int = 1024
    snowflake: bytes = None
    message_constructor: t.Callable = None
    snowflake_constructor: t.Callable = None

    def __post_init__(self):
        snowflake_constructor = self.snowflake_constructor
        if snowflake_constructor is None:
            snowflake_constructor = packet_snowflake
        self.snowflake = snowflake_constructor(self)

    def chunks(self) -> t.Generator[Chunk, None, None]:
        for i in range(self.chunk_count):
            chunk_data = self.data[i * self.chunk_size: (i + 1) * self.chunk_size]
            yield Chunk(
                i,
                self.chunk_count,
                chunk_data,
                self.snowflake
            )

    @property
    def chunk_count(self) -> int:
        return len(self.data) // self.chunk_size + 1

    @staticmethod
    def from_chunks(snowflake: bytes, chunks: t.Iteratable[Chunk]):
        message_constructor = Chunk.message_constructor
        if message_constructor is None:
            message_constructor = RawMessage
        chunks = sorted(chunks, key=lambda chunk: chunk.index)
        data = b"".join([chunk.chunk_data for chunk in chunks]) 
        return message_constructor(data, snowflake=snowflake)



class ChunkReception(dict):
    def feed(self, chunk: Chunk) -> None:
        if chunk.message_id not in self:
            self[chunk.message_id]["total"] = chunk.total
        self[chunk.message_id]["chunks"][chunk.index] = chunk

    def __iter__(self):
        """The chunk candidates are running for chunk president.""" # Please leave this in LOL THIS IS TOO GOOD NOT TO
        for key, chunk_candidate in self.values():
            if len(chunk_candidate["chunks"]) == chunk_candidate["total"]:
                yield Chunk.from_chunks(chunk_candidate["chunks"])
                del self[key]    


