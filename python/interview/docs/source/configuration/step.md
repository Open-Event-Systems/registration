# Step

A _step_ is an action taken as part of an interview. There are multiple kinds of steps
that will be detailed below.

## Ask

The `ask` step asks a question.

Properties:

`ask` (required)
: The ID of the question to ask.

```{note}
Even though it seems essential, you might not have to use this step very often.

The interview process will automatically search for and ask the appropriate questions
to gather the required information.
```

You may find it useful to apply `when` conditions to this step to only ask a question in
certain circumstances.

```{note}
Each question will only be asked once, even if there is an explicit `ask` step.
```

```{warning}
When defining an explicit `ask` step, the `when` conditions defined *on the question* are
**not** considered.

The specified question will be asked when the `when` conditions *on the ``ask`` step* pass.
```

Example:

```yaml
# Ask the `preferred-name` question only when the user has indicated they have a preferred
# name.
- ask: preferred-name
  when: person.uses_preferred_name
```

## Set

The `set` step assigns a value to a variable in the interview state. This is meant to
derive information from other values provided by user responses.

Properties:

`set` (required)
: The variable to assign.

`value` (required)
: The value to assign. This will be evaluated as a Jinja2 expression.

`always`
: Set this to `true` to assign the variable even if it is already defined. Normally, the
`set` step does nothing if the variable already exists. Defaults to `false`.

Example:

```yaml
# Sets the person's display name to either their preferred name or their first name
- set: person.display_name
  value: person.preferred_name or person.first_name
```

```{warning}
The `value` field is evaluated as a Jinja2 expression.
If you want to provide a constant string, you must wrap it in multiple quotes,
like `value: "'example'"`.
```

## Exit

The `exit` step ends the interview without completing. This is only useful when combined
with `when` conditions.

Properties:

`exit` (required)
: The title of the exit step. This is evaluated as a Jinja2 template.

`description`
: An optional message describing the exit reason. This is evaluated as a Jinja2
template. User interfaces may parse this as Markdown.

Example:

```yaml
- exit: Not Old Enough
  description: You must be at least **21** years of age to enter.
  when: person.birth_date | age < 21
```

## Eval

Ensures the given variables are defined. This is meant to be used as an easy way to
trigger all the questions needed to gather the given values.

Properties:

`eval` (required)
: A Jinja2 expression, or list of Jinja2 expressions to evaluate.
