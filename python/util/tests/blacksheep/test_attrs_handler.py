from typing import Optional, Union

import pytest
from attrs import frozen
from blacksheep import Application, Response
from blacksheep.server.openapi.common import ContentInfo, ResponseInfo
from blacksheep.server.openapi.v3 import FieldInfo, OpenAPIHandler
from cattrs.preconf.orjson import make_converter
from oes.util import is_attrs_instance
from oes.util.blacksheep import JSONResponseFunc
from oes.util.blacksheep.attrs_handler import (
    AttrsTypeHandler,
    FromAttrs,
    _get_field_type,
)
from openapidocs.v3 import Info, Reference, Schema, ValueFormat, ValueType

app = Application()

app_docs = OpenAPIHandler(
    info=Info(
        title="Test",
        version="0.1.0",
    )
)

app_docs.object_types_handlers.append(AttrsTypeHandler(app_docs))

app_docs.bind_app(app)

converter = make_converter()


def _default(obj):
    if is_attrs_instance(obj):
        return converter.unstructure(obj)
    else:
        raise TypeError


json_response = JSONResponseFunc(default=_default)


@frozen
class MyClass1:
    a: int
    b: Optional[str] = None


@frozen
class MyClass2:
    c: int


@frozen
class MyClass3:
    val: int
    obj: Union[MyClass1, MyClass2]


@frozen
class MyClass4:
    val: Optional[list[Union[MyClass2, str]]]
    val2: tuple[Union[str, MyClass2, None]]
    val3: dict[str, int]


my_class_1_schema = Schema(
    type=ValueType.OBJECT,
    nullable=False,
    properties={
        "a": Schema(
            type=ValueType.INTEGER,
            format=ValueFormat.INT64,
            nullable=False,
        ),
        "b": Schema(
            type=ValueType.STRING,
            nullable=True,
        ),
    },
    required=["a"],
)

my_class_2_schema = Schema(
    type=ValueType.OBJECT,
    nullable=False,
    properties={
        "c": Schema(
            type=ValueType.INTEGER,
            format=ValueFormat.INT64,
            nullable=False,
        ),
    },
    required=["c"],
)

my_class_3_schema = Schema(
    type=ValueType.OBJECT,
    nullable=False,
    properties={
        "val": Schema(
            type=ValueType.INTEGER,
            format=ValueFormat.INT64,
            nullable=False,
        ),
        "obj": Schema(
            one_of=[
                my_class_1_schema,
                my_class_2_schema,
            ],
            nullable=False,
        ),
    },
    required=["val", "obj"],
)

my_class_4_schema = Schema(
    type=ValueType.OBJECT,
    nullable=False,
    properties={
        "val": Schema(
            type=ValueType.ARRAY,
            items=Schema(
                one_of=[
                    my_class_2_schema,
                    Schema(type=ValueType.STRING, nullable=False),
                ],
                nullable=False,
            ),
            nullable=True,
        ),
        "val2": Schema(
            type=ValueType.ARRAY,
            items=Schema(
                one_of=[
                    Schema(type=ValueType.STRING, nullable=False),
                    my_class_2_schema,
                ],
                nullable=True,
            ),
            nullable=False,
        ),
        "val3": Schema(
            type=ValueType.OBJECT,
            nullable=False,
        ),
    },
    required=["val2", "val3"],
)


@app.router.post("/")
@app_docs(
    summary="Test endpoint",
    responses={
        200: ResponseInfo(
            "Example response",
            content=[
                ContentInfo(
                    type=MyClass4,
                )
            ],
        )
    },
)
def view(body: FromAttrs[MyClass4]) -> Response:
    """Example view."""
    return json_response(body.value)


@pytest.fixture
def docs():
    docs_obj = OpenAPIHandler(
        info=Info(
            title="Test",
            version="0.1.0",
        )
    )
    docs_obj.object_types_handlers.append(AttrsTypeHandler(docs_obj))
    return docs_obj


@pytest.mark.parametrize(
    "typ, expected",
    (
        (
            MyClass1,
            my_class_1_schema,
        ),
        (
            MyClass2,
            my_class_2_schema,
        ),
        (
            MyClass3,
            my_class_3_schema,
        ),
        (
            MyClass4,
            my_class_4_schema,
        ),
    ),
)
def test_get_field_type(docs, typ, expected):
    assert _get_field_type(docs, typ) == expected


def test_attrs_handler(docs: OpenAPIHandler):
    ref = docs.get_schema_by_type(MyClass3)
    assert isinstance(ref, Reference)

    assert docs.get_fields(MyClass3) == [
        FieldInfo(
            "val",
            Schema(
                type=ValueType.INTEGER,
                format=ValueFormat.INT64,
                nullable=False,
            ),
        ),
        FieldInfo(
            "obj",
            Schema(
                one_of=[
                    my_class_1_schema,
                    my_class_2_schema,
                ],
                nullable=False,
            ),
        ),
    ]
