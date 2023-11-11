import { DateField } from "#src/components/fields/date/DateField"
import { NumberField } from "#src/components/fields/number/NumberField"
import { SelectField } from "#src/components/fields/select/SelectField"
import { TextField } from "#src/components/fields/text/TextField"
import { FieldProps } from "#src/types"
import { JSONSchema } from "@open-event-systems/interview-lib"
import { ElementType } from "react"

/**
 * Renders the appropriate component for a field.
 */
export const Field = (props: FieldProps<unknown>) => {
  const schema = props.state.schema

  const Component = getComponentForField(schema)

  if (Component) {
    return <Component {...props} />
  } else {
    return null
  }
}

const getComponentForField = (
  schema: JSONSchema,
): ElementType<FieldProps<unknown>> | null => {
  if (typeof schema == "boolean") {
    return null
  }

  const fieldType = schema["x-type"]

  let component = null

  switch (fieldType) {
    case "text":
      component = TextField
      break
    case "number":
      component = NumberField
      break
    case "select":
      component = SelectField
      break
    case "date":
      component = DateField
      break
  }

  // need to figure out better typing for all this
  return component as ElementType<FieldProps<unknown>> | null
}
