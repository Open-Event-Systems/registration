"""Main entry point."""

import asyncio

import aio_pika
import jinja2
import orjson
import typed_settings as ts
from aio_pika.abc import AbstractChannel, AbstractExchange
from loguru import logger
from oes.email.config import Config
from oes.email.sender import EmailSender, get_sender
from oes.email.template import Attachments, get_environment, render_message
from oes.email.types import Email
from oes.utils import setup_logging
from oes.utils.config import get_loaders


@ts.cli(Config, loaders=get_loaders("OES_EMAIL_", ("email.yml",)))
def main(config: Config):
    """Main entry point."""
    setup_logging(config.debug)
    asyncio.run(_main(config))


async def _main(config: Config):
    sender = get_sender(config.use)
    env = get_environment(config.template_path)

    conn = await aio_pika.connect_robust(config.amqp_url, fail_fast=False)

    async with conn:
        channel = await conn.channel()
        exchange = await channel.declare_exchange(
            "email", type=aio_pika.ExchangeType.TOPIC, durable=True
        )
        await channel.set_qos(prefetch_count=1)

        consumers = [
            asyncio.create_task(
                _consume(channel, exchange, email_type, config, sender, env)
            )
            for email_type in config.messages
        ]
        await asyncio.gather(*consumers)


async def _consume(
    channel: AbstractChannel,
    exchange: AbstractExchange,
    email_type: str,
    config: Config,
    sender: EmailSender,
    env: jinja2.Environment,
):
    queue = await channel.declare_queue(f"email.{email_type}", durable=True)
    await queue.bind(exchange, f"email.{email_type}")
    async with queue.iterator() as queue_iter:
        logger.debug(f"Consuming from email.{email_type}")
        async for item in queue_iter:
            async with item.process():
                data = orjson.loads(item.body)
                email = await asyncio.to_thread(
                    _make_email, config, env, email_type, data
                )
                logger.info(f"Sending {email_type} email to {email.to}")
                await sender(email, config)


def _make_email(
    config: Config,
    env: jinja2.Environment,
    email_type: str,
    body: dict,
) -> Email:
    msg_config = config.messages[email_type]
    to: str = body.get("email", "")
    attachments = Attachments(config.template_path)

    from_ = msg_config.email_from or config.email_from
    res = render_message(
        env, to, from_, msg_config.subject, attachments, email_type, body
    )

    email = Email(
        to=res.to,
        from_=res.from_,
        subject=res.subject,
        text=res.text,
        html=res.html,
        attachments=tuple(attachments),
    )

    return email
