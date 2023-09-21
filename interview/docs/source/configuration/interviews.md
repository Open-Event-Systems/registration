# Interview

Interviews are defined in the `interviews.yml` configuration file.

The configuration file is a mapping containing a key `interviews` which is a list of
interview objects.

Properties:

`id` (required)
: An ID for the interview. This must be unique.

`title`
: The title of the interview.

`questions` (required)
: A list of question objects, or paths to `.yml` files containing a list of questions.

Relative paths are resolved relative to the interviews configuration file.

`steps` (required)
: A list of step objects in the interview.

Example:

```yaml
# interviews.yml
---
interviews:
  - id: interview1
    title: Interview 1
    questions:
      - questions/simple.yml
      - id: person-name
        fields:
          - type: text
            set: person.name
            label: Name
    steps:
      - ask: person-name
      - exit: No Homers Club
        description: No Homers allowed
        when: person.name == "Homer"
```

```{note}
In the above example, the explicit `ask` for `person-name` isn't actually necessary,
it would have been asked automatically. More on that later.
```
