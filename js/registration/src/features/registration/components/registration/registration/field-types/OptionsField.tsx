import { createField } from "#src/features/registration/components/registration/registration/field-types/Base"
import { MultiSelect, Text } from "@mantine/core"

export const OptionsField = createField<string[]>(
  ({ label, event, value, setValue }) => {
    const options = event
      ? event.registration_options.map((o) => ({ value: o.id, label: o.name }))
      : value
      ? value.map((o) => ({ value: o, label: o }))
      : []

    return (
      <MultiSelect
        aria-label={label}
        data={options}
        value={value}
        placeholder="Options"
        onChange={(v) => {
          setValue(v)
        }}
      />
    )
  },
  ({ value = [], event }) => {
    const optNames = new Map<string, string>()

    for (const opt of event?.registration_options ?? []) {
      optNames.set(opt.id, opt.name)
    }

    const options = value.map((o) => optNames.get(o) || o).join(", ")
    return <Text>{options}</Text>
  },
)
