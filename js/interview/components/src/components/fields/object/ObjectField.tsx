import { Field } from "#src/components/fields/Field.js"
import { Stack, StackProps, useProps } from "@mantine/core"
import { FieldState, ObjectFieldState } from "@open-event-systems/interview-lib"
import { observer } from "mobx-react-lite"

export type ObjectFieldProps = {
  state: ObjectFieldState
} & Omit<StackProps, "children">

export const ObjectField = observer((props: ObjectFieldProps) => {
  const { state, ...other } = useProps("OESIObjectField", {}, props)

  const fields = Object.entries(state.properties ?? {})
    .filter((e): e is [string, FieldState<unknown>] => !!e[1])
    .map(([prop, state]) => <Field key={prop} state={state} />)

  return (
    <Stack
      classNames={{
        root: "OESIObjectField-root",
      }}
      {...other}
    >
      {fields}
    </Stack>
  )
})

ObjectField.displayName = "ObjectField"
