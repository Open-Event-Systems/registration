# Question

Questions are defined as YAML documents containing an array of question objects.

Properties:

`id` (required)

: The question ID. This must be unique among all questions included in an interview.

`title`
: The question title. This will be evaluated as a Jinja2 template.

`description`
: The question text itself. This will be evaluated as a Jinja2 template. User interfaces
may interpret this using Markdown syntax.

`fields`
: The list of fields.

`buttons`
: Optional list of button objects to override the default "next" button on each
question.

`buttons_set`
: The variable to set with the pressed button value.

## Example

```yaml
---
- id: a-question-id
  title: Question Title
  description: |
    A question description.

    Descriptions may contain **markdown**.

  fields:
    # Individual fields, specifying type, the value they set, and
    # field-specific configuration
    - set: person.first_name
      type: text
      label: First Name

    - set: person.last_name
      type: text
      label: Last Name

    - set: person.preferred_name
      type: text
      optional: true
      label: Preferred Name

  # Optionally override the buttons shown
  buttons:
    - label: "Yes"
      value: 1
      primary: true
      default: true
    - label: "No"
      value: 0

  # Optionally store the value of the button pressed
  buttons_set: clicked_yes

  # Conditions restricting when this question may be asked
  when:
    - need_person_info is true
```
