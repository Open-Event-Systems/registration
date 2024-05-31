from pathlib import Path

from jinja2.utils import Namespace
from oes.email.template import Attachments, get_environment, render_template
from oes.email.types import Attachment, AttachmentType


def test_template():
    attachments = Attachments(Path("tests/email/templates"))

    env = get_environment(Path("tests/email/templates"))

    ns = Namespace(
        {
            "to": "to@test.com",
            "from": "from@test.com",
            "subject": "Test",
        }
    )

    res = render_template(env, ns, attachments, "template.txt", {"text": "Test text."})

    assert res == "Test\n\nTest text."


def test_template_attachments():
    ns = Namespace(
        {
            "to": "to@test.com",
            "from": "from@test.com",
            "subject": "Test",
        }
    )
    attachments = Attachments(Path("tests/email/templates"))

    env = get_environment(Path("tests/email/templates"))

    res = render_template(env, ns, attachments, "attachment.txt", {})

    assert res == "Attachment: attachment1"
    attached_objs = list(attachments)
    assert len(attached_objs) == 1
    assert attached_objs[0] == Attachment(
        id="attachment1",
        name="attachment.txt",
        data=b'Attachment: {{ attach("attachment.txt") }}\n',
        media_type="text/plain",
        attachment_type=AttachmentType.attachment,
    )


def test_template_attachments_inline():
    ns = Namespace(
        {
            "to": "to@test.com",
            "from": "from@test.com",
            "subject": "Test",
        }
    )
    attachments = Attachments(Path("tests/email/templates"))

    env = get_environment(Path("tests/email/templates"))

    res = render_template(env, ns, attachments, "inline.txt", {})

    assert res == "Attachment: attachment1"
    attached_objs = list(attachments)
    assert len(attached_objs) == 1
    assert attached_objs[0] == Attachment(
        id="attachment1",
        name="inline.txt",
        data=b'Attachment: {{ inline("inline.txt") }}\n',
        media_type="text/plain",
        attachment_type=AttachmentType.inline,
    )


def test_template_subject():
    ns = Namespace(
        {
            "to": "to@test.com",
            "from": "from@test.com",
            "subject": "Original",
        }
    )
    attachments = Attachments(Path("tests/email/templates"))

    env = get_environment(Path("tests/email/templates"))
    res = render_template(env, ns, attachments, "subject.txt", {})
    assert ns.subject == "Subject"
    assert res == ("Subject is Original\nSubject is Subject")
