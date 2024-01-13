import { Select } from "@mantine/core"

export type StationSelectProps = {
  options: string[]
  value?: string | null
  onChange?: (value: string | null) => void
}

export const StationSelect = (props: StationSelectProps) => {
  const { options, value, onChange } = props
  return (
    <Select
      classNames={{
        root: "StationSelect-root",
      }}
      size="xs"
      placeholder="Station ID"
      value={value}
      data={options.map((o) => ({
        label: `Station ${o}`,
        value: o,
      }))}
      onChange={(o) => {
        onChange && onChange(o)
      }}
    />
  )
}
