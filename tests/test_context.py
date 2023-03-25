import asyncio

import pytest
from unittest.mock import AsyncMock, MagicMock

from botislav.context import Context, Cache, ContextManager


@pytest.fixture
def message():
    mock = AsyncMock()
    mock.content = "text"
    return mock


@pytest.fixture
def client():
    mock = MagicMock()
    return mock


@pytest.fixture
def context(message, client):
    return Context(
        key="test",
        message=message,
        reply_queue=asyncio.Queue(),
        cache=Cache(steam_id="steam_id", opendota_id=123456),
        client=client
    )


@pytest.fixture
def cache():
    mock = MagicMock()
    mock.get.return_value = None
    return mock


@pytest.fixture
def context_manger(cache, client):
    manger = ContextManager(cache=cache)
    manger.set_client(client)
    return manger


@pytest.mark.asyncio
async def test_context_text(context: Context, message: AsyncMock):
    assert context.user_text == "text"


@pytest.mark.asyncio
async def test_context_reply_to_user(context: Context, message: AsyncMock):
    await context.reply_to_user("foo")
    message.reply.assert_awaited_with("foo")


@pytest.mark.asyncio
async def test_context_send_text(context: Context, message: AsyncMock):
    await context.send_text("foo")
    message.channel.send.assert_awaited_with("foo")


@pytest.mark.asyncio
async def test_exception_in_context_removes_it_from_active(context_manger: ContextManager, message: AsyncMock):

    class SomeError(Exception):
        pass

    with pytest.raises(SomeError):
        with context_manger.get_context("foo", message):
            raise SomeError

    assert not context_manger.has_active_context("foo")


@pytest.mark.asyncio
async def test_context_waits_for_user_reply_timeout(context_manger: ContextManager, message: AsyncMock):

    with context_manger.get_context("foo", message) as context:
        replied = await context.wait_for_user_reply(1)

    assert not replied


@pytest.mark.asyncio
async def test_context_waits_for_user_reply_success(context_manger: ContextManager, message: AsyncMock):
    replied = False

    async def _dialog():
        with context_manger.get_context("foo", message) as context:
            nonlocal replied
            replied = await context.wait_for_user_reply(5)

    asyncio.create_task(_dialog())

    await asyncio.sleep(0.1)

    context_manger.pass_reply_to_active_context("foo", message)

    await asyncio.sleep(0.1)

    assert replied
