import { CheckboxSelectField } from "#src/components/fields/select/Checkbox"
import { DropdownSelectField } from "#src/components/fields/select/Dropdown"
import { RadioSelectField } from "#src/components/fields/select/Radio"
import { FieldProps } from "#src/types"

export type SelectFieldProps = FieldProps<string | string[]>

export const SelectField = (props: SelectFieldProps) => {
  const { state } = props

  switch (state.schema["x-component"]) {
    case "radio":
      return <RadioSelectField {...props} />
    case "checkbox":
      return <CheckboxSelectField {...props} />
    default:
      return <DropdownSelectField {...props} />
  }
}
