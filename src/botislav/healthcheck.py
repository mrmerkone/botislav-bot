import asyncio

from attr import dataclass
from discord import Client


@dataclass
class _ClientContext:
    client: Client

    def handle_socket_client(
        self, _reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        message = b"ok"

        if (
            self.client.user is None
            or not self.client.is_ready()
            or self.client.is_closed()
        ):
            message = b"failed"

        writer.write(message)
        writer.close()


def start(client: Client, port: int = 8080) -> asyncio.base_events.Server:
    ctx = _ClientContext(client)
    return asyncio.run(
        asyncio.start_server(ctx.handle_socket_client, "127.0.0.1", port)
    )
