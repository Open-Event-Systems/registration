"""Message queue module."""

import asyncio
from collections.abc import Mapping
from contextlib import suppress
from typing import Any

import aio_pika
import orjson
from loguru import logger
from oes.auth.config import Config


class MQService:
    """Message queue service."""

    def __init__(self, config: Config):
        self.config = config
        self.ready = False

    async def start(self):
        self.run_task = asyncio.create_task(self._run())

    async def _run(self):
        conn = await aio_pika.connect_robust(
            self.config.amqp_url,
            fail_fast=False,
        )
        async with conn:
            channel = await conn.channel()
            self.exchange = await channel.declare_exchange(
                "email", type=aio_pika.ExchangeType.TOPIC, durable=True
            )
            self.queue = await channel.declare_queue("email.auth", durable=True)
            await self.queue.bind(self.exchange, "email.auth")
            self.ready = True
            logger.debug("AMQP connected")
            while True:
                await asyncio.sleep(3600)

    async def publish(self, body: Mapping[str, Any]):
        msg = aio_pika.Message(
            orjson.dumps(body), delivery_mode=aio_pika.DeliveryMode.PERSISTENT
        )
        await self.exchange.publish(msg, "email.auth")

    async def stop(self):
        self.run_task.cancel()
        with suppress(asyncio.CancelledError):
            await self.run_task
