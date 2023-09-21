from unittest.mock import MagicMock

from blacksheep.server.openapi.common import (
    ContentInfo,
    ParameterInfo,
    RequestBodyInfo,
    ResponseInfo,
)
from oes.util.blacksheep.docs import DocsHelper


class MyResponse:
    pass


def test_docs_helper():
    orig_docs = MagicMock()

    docs = DocsHelper(orig_docs)

    @docs(
        summary="Summary",
        description="Description",
        tags=["Test"],
        status_code=200,
        response_type=MyResponse,
        response_summary="The response",
        parameters={
            "test": ParameterInfo("test"),
        },
        request_body=RequestBodyInfo("test"),
        responses={404: ResponseInfo("The resource was not found.")},
        ignored=False,
        deprecated=False,
    )
    def func():
        pass

    orig_docs.assert_called_with(
        summary="Summary",
        description="Description",
        tags=["Test"],
        parameters={
            "test": ParameterInfo("test"),
        },
        request_body=RequestBodyInfo("test"),
        responses={
            200: ResponseInfo(
                "The response",
                content=[
                    ContentInfo(
                        type=MyResponse,
                    ),
                ],
            ),
            404: ResponseInfo("The resource was not found."),
        },
        ignored=False,
        deprecated=False,
        on_created=None,
    )
