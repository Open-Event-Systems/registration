import { scopeDescriptions } from "#src/features/auth/components/device/scopes/scope"
import { Checkbox, Stack } from "@mantine/core"

export type ScopeSelectProps = {
  selected?: string[]
  onChange?: (selected: string[]) => void
}

export const ScopeSelect = (props: ScopeSelectProps) => {
  const { selected, onChange } = props

  const knownValues = selected?.filter((v) => v in scopeDescriptions)
  const extraValues = selected?.filter((v) => !knownValues?.includes(v))

  return (
    <Checkbox.Group
      value={knownValues}
      onChange={(values) => {
        onChange && onChange([...values, ...(extraValues ?? [])])
      }}
    >
      <Stack>
        {Object.entries(scopeDescriptions).map(([scope, desc]) => (
          <Checkbox key={scope} value={scope} label={desc} />
        ))}
      </Stack>
    </Checkbox.Group>
  )
}
