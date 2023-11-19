import { createField } from "#src/features/registration/components/registration/registration/field-types/Base"
import { Text, TextInput } from "@mantine/core"

export const TextField = createField<string>(
  ({ value, label, setValue }) => (
    <TextInput
      aria-label={label}
      value={value}
      onChange={(e) => {
        setValue(e.target.value)
      }}
    />
  ),
  ({ value }) => <Text>{value}</Text>,
)
