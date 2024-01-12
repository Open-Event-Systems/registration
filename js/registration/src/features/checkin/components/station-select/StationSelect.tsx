import { Select } from "@mantine/core"

export type StationSelectProps = {
  options: string[]
  onChange?: (value: string | null) => void
}

export const StationSelect = (props: StationSelectProps) => {
  const { options, onChange } = props
  return (
    <Select
      classNames={{
        root: "StationSelect-root",
      }}
      size="xs"
      placeholder="Station ID"
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
