import asyncio

import discord


class _ClientContext:
    """A simple class to keep context for the client handler function"""

    def __init__(self, client: discord.client, bot_max_latency: float):
        self.client = client
        self.bot_max_latency = bot_max_latency

    def handle_socket_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        message = b"healthy"

        if (
            self.client.latency > self.bot_max_latency  # Latency too high
            or self.client.user is None  # Not logged in
            or not self.client.is_ready()  # Client’s internal cache not ready
            or self.client.is_closed()  # The websocket connection is closed
        ):
            message = b"unhealthy"

        writer.write(message)
        writer.close()


def start(
    client: discord.client, port: int = 8080, bot_max_latency: float = 0.5
) -> asyncio.base_events.Server:
    host = "127.0.0.1"
    ctx = _ClientContext(client, bot_max_latency)
    return client.loop.run_until_complete(
        asyncio.start_server(ctx.handle_socket_client, host, port)
    )
