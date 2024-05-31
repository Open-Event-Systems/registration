"""Configuration."""

from enum import Enum
from pathlib import Path

import typed_settings as ts


class EmailSenderType(str, Enum):
    """An email sender type."""

    mock = "mock"
    smtp = "smtp"
    mailgun = "mailgun"


@ts.settings(kw_only=True)
class SMTPSettings:
    """SMTP settings."""

    server: str = ts.option(default="localhost", help="the server address")
    port: int = ts.option(default=587, help="the SMTP port")

    tls: str | None = ts.option(default="starttls", help="the SSL/TLS method")

    username: str = ts.option(default="", help="the SMTP username")

    password: ts.SecretStr = ts.secret(default="", help="the SMTP password")


@ts.settings(kw_only=True)
class MailgunSettings:
    """Mailgun settings."""

    domain: str = ts.option(help="the domain to send from")
    api_key: ts.SecretStr = ts.secret(help="the API key")
    base_url: str = ts.option(
        default="https://api.mailgun.net", help="the base mailgun API URL"
    )


@ts.settings
class MessageConfig:
    """Per message type configuration."""

    subject: str = ts.option(help="the email subject")
    email_from: str | None = ts.option(help="the email from address", default=None)


@ts.settings
class Config:
    """Config."""

    email_from: str = ts.option(help="the default from address")
    messages: dict[str, MessageConfig] = ts.option(
        help="per message config", factory=dict
    )
    amqp_url: str = ts.option(
        help="the amqp server URL", default="amqp_url: amqp://guest:guest@localhost/"
    )
    debug: bool = ts.option(help="debug output", default=False)

    template_path: Path = ts.option(
        default=Path("templates"), help="path to the email template directory."
    )

    use: EmailSenderType = ts.option(
        default=EmailSenderType.mock, help="the implementation to use"
    )

    smtp: SMTPSettings | None = ts.option(default=None, help="SMTP settings")
    mailgun: MailgunSettings | None = ts.option(default=None, help="Mailgun settings")
