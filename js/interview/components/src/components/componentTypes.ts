import { DateField } from "#src/components/fields/DateField.js"
import { NumberField } from "#src/components/fields/NumberField.js"
import { ObjectField } from "#src/components/fields/ObjectField.js"
import { SelectField } from "#src/components/fields/SelectField.js"
import { TextField } from "#src/components/fields/TextField.js"
import { FieldProps } from "#src/types.js"
import { FieldTypes, Schema } from "@open-event-systems/interview-lib"
import { ComponentType } from "react"

const componentTypes: { [K in keyof FieldTypes]?: ComponentType<FieldProps> } =
  {
    text: TextField,
    number: NumberField,
    date: DateField,
    select: SelectField,
  }

/**
 * Get the component for a field type.
 */
export const getComponentForField = (
  schema: Schema,
): ComponentType<FieldProps> | null => {
  const schemaType = schema.type
  const fieldType = schema["x-type"]

  // special case, don't render button fields even though they are in the schema
  if (fieldType == "button") {
    return null
  }

  let component

  if (fieldType) {
    component = componentTypes[fieldType]
  } else if (schemaType == "object") {
    component = ObjectField
  }

  if (component) {
    return component
  } else {
    throw new Error(`Unsupported field type: ${fieldType}`)
  }
}
