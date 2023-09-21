"""Docs helpers."""
from blacksheep.server.openapi.v3 import OpenAPIHandler
from oes.interview.input.question import Question
from oes.interview.interview.interview import Interview
from oes.util.blacksheep import AttrsTypeHandler, DocsHelper
from openapidocs.v3 import (
    HTTPSecurity,
    Info,
    OpenAPI,
    Schema,
    Security,
    SecurityRequirement,
    ValueFormat,
    ValueType,
)

docs = OpenAPIHandler(
    info=Info(
        title="Interview Service",
        version="0.2",
    ),
)
"""The docs handler."""

docs_helper = DocsHelper(docs)
"""The docs helper decorator."""

responses_schema = Schema(
    type=ValueType.OBJECT,
    properties={
        "field_0": Schema(
            type=ValueType.STRING,
            example="Firstname",
        ),
        "field_1": Schema(
            type=ValueType.STRING,
            example="Lastname",
        ),
    },
    nullable=True,
)

update_form_data_schema = Schema(
    type=ValueType.OBJECT,
    properties={
        "responses": responses_schema,
        "state": Schema(
            type=ValueType.STRING,
            format=ValueFormat.BINARY,
        ),
    },
    required=["state"],
)

update_json_schema = Schema(
    type=ValueType.OBJECT,
    properties={
        "responses": responses_schema,
        "state": Schema(type=ValueType.STRING, example="Wq4t2aBO8Db97;JWd"),
    },
    required=["state"],
)


question_schema = Schema(
    type=ValueType.OBJECT,
    properties={
        "id": Schema(type=ValueType.STRING),
        "title": Schema(type=ValueType.STRING, nullable=True),
        "description": Schema(type=ValueType.STRING, nullable=True),
        "fields": Schema(
            type=ValueType.ARRAY,
            items=Schema(type=ValueType.OBJECT),
        ),
        "when": Schema(type=ValueType.STRING),
    },
    required=["id", "fields", "when"],
)

interview_schema = Schema(
    type=ValueType.OBJECT,
    properties={
        "id": Schema(type=ValueType.STRING),
        "title": Schema(type=ValueType.STRING, nullable=True),
        "questions": Schema(
            type=ValueType.ARRAY,
            items=question_schema,
        ),
        "steps": Schema(
            type=ValueType.ARRAY,
            items=Schema(type=ValueType.OBJECT),
        ),
    },
    required=["id", "questions", "steps"],
)

interview_state_result_schema = Schema(
    type=ValueType.OBJECT,
    properties={
        "interview": interview_schema,
        "target_url": Schema(type=ValueType.STRING),
        "submission_id": Schema(type=ValueType.STRING),
        "expiration_date": Schema(type=ValueType.STRING, format=ValueFormat.DATETIME),
        "complete": Schema(type=ValueType.BOOLEAN),
        "context": Schema(type=ValueType.OBJECT),
        "data": Schema(type=ValueType.OBJECT),
    },
)

docs.set_type_schema(Question, question_schema)
docs.set_type_schema(Interview, interview_schema)


incomplete_interview_state_json_schema = Schema(
    type=ValueType.OBJECT,
    properties={
        "content": Schema(type=ValueType.OBJECT),
        "update_url": Schema(type=ValueType.STRING),
        "state": Schema(type=ValueType.STRING),
    },
    required=["content", "update_url", "state"],
)

complete_interview_state_json_schema = Schema(
    type=ValueType.OBJECT,
    properties={
        "complete": Schema(type=ValueType.BOOLEAN, example=True),
        "target_url": Schema(type=ValueType.STRING),
        "state": Schema(type=ValueType.STRING),
    },
    required=["complete", "target_url", "state"],
)

interview_state_json_schema = Schema(
    one_of=[
        incomplete_interview_state_json_schema,
        complete_interview_state_json_schema,
    ],
)


docs.components.security_schemes = {
    "apiKey": HTTPSecurity(
        scheme="bearer",
    )
}

docs.object_types_handlers.append(AttrsTypeHandler(docs))


@docs.events.on_docs_created
def _handle_docs(handler: OpenAPIHandler, docs: OpenAPI):
    # use auth in swagger UI
    docs.security = Security(
        requirements=[
            SecurityRequirement("apiKey", []),
        ]
    )
