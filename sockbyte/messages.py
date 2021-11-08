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

    def bytes(self):
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
        return Chunk(*fields)


@dataclass()
class RawMessage:
    data: bytes
    chunk_size: int = 1024
    snowflake: bytes = None
    message_constructor: t.Callable = field(default=None, repr=False)
    snowflake_constructor: t.Callable = field(default=None, repr=False)

    def __post_init__(self):
        snowflake_constructor = self.snowflake_constructor
        if snowflake_constructor is None:
            snowflake_constructor = packet_snowflake
        self.snowflake = snowflake_constructor(self)

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


class ChunkReception(dict):
    def feed(self, chunk: Chunk) -> None:
        if chunk.message_id not in self:
            self[chunk.message_id]["total"] = chunk.total
        self[chunk.message_id]["chunks"].append(chunk)

    def fetch(self):
        """The chunk candidates are running for chunk president.""" # Please leave this in LOL THIS IS TOO GOOD NOT TO
        for key, chunk_candidate in self.items():
            if len(chunk_candidate["chunks"]) == int(chunk_candidate["total"]):
                message = RawMessage.from_chunks(key, chunk_candidate["chunks"])
                self[key]["completed"] = True
                break
        for key in list(self.keys()):
            if self[key]["completed"] is True:
                del self[key]
        return message

    def __missing__(self, key: bytes):
        self[key] = {"total": None, "chunks": [], "completed": False}
        return self[key]
