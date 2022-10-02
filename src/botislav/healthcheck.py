from attr import dataclass
from discord import Client
from aiohttp import web


@dataclass
class ClientHealthStatus:
    client: Client

    async def __call__(self, request: web.Request) -> web.Response:
        message = "ok"

        if (
            self.client.user is None
            or not self.client.is_ready()
            or self.client.is_closed()
        ):
            message = "failed"

        return web.Response(text=message)


async def start(client: Client, port: int = 8080):
    app = web.Application()
    app.add_routes([web.get('/', ClientHealthStatus(client))])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", port)
    await site.start()


