import { MultiSelect, MultiSelectProps, useProps } from "@mantine/core"

type Option = {
  id: string
  label?: string
}

export type OptionsFieldProps = {
  options?: Option[]
  selectedOptions?: string[]
} & Omit<MultiSelectProps, "data" | "value">

export const OptionsField = (props: OptionsFieldProps) => {
  const {
    options = [],
    selectedOptions,
    readOnly,
    ...other
  } = useProps("OptionsField", {}, props)

  const editable = !!other.onChange

  return (
    <MultiSelect
      placeholder="Options"
      readOnly={readOnly ?? editable}
      {...other}
      aria-label="Options"
      value={selectedOptions}
      data={options.map((o) => ({
        value: o.id,
        label: o.label || o.id,
      }))}
    />
  )
}
