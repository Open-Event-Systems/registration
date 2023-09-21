# Field

A field in a question. The exact properties of each field object depends on its type,
but these are the properties common to all fields:

Properties:

`type` (required)
: A string describing the field type.

`set`
: The variable to store the value of this field in.

`optional`
: Whether `None` or "null" is an allowed value. Defaults to `false`.

`default`
: The default value of this field. This is only used by user interfaces to pre-fill the
input, it does not change the behavior of the field validation.

`label`
: An optional label for the input field. This will be evaluated a Jinja2 template.
