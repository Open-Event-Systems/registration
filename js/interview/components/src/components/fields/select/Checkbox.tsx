import { getOptions, isNullable } from "#src/components/fields/select/util.js"
import { FieldProps } from "#src/types.js"
import { observer } from "mobx-react-lite"

import {
  Checkbox,
  CheckboxGroupProps,
  CheckboxProps,
  Stack,
  useProps,
} from "@mantine/core"

export type CheckboxSelectFieldProps = FieldProps<string | string[]> &
  Omit<CheckboxGroupProps, "error" | "value" | "onChange" | "children"> & {
    CheckboxProps?: Partial<CheckboxProps>
  }

export const CheckboxSelectField = observer(
  (props: CheckboxSelectFieldProps) => {
    const { state, CheckboxProps, ...other } = useProps(
      "OESICheckboxSelectField",
      {},
      props,
    )

    const options = getOptions(state.schema)
    const hasError = !state.isValid && state.touched
    const nullable = isNullable(state.schema)

    const value = (
      Array.isArray(state.value) ? state.value : [state.value]
    ).filter((v): v is string => !!v)

    return (
      <Checkbox.Group
        classNames={{
          root: "OESICheckboxSelectField-root",
        }}
        required={!nullable}
        withAsterisk={!nullable}
        label={state.schema.title}
        {...other}
        error={hasError ? state.error : undefined}
        value={value || []}
        onChange={(e) => {
          state.setValue(e)
          state.setTouched()
        }}
      >
        <Stack
          classNames={{
            root: "OESICheckboxSelectField-group",
          }}
        >
          {options.map((opt) => (
            <Checkbox
              key={opt.value}
              classNames={{
                root: "OESICheckboxSelectField-checkbox-root",
              }}
              value={opt.value}
              {...CheckboxProps}
              label={opt.label}
            />
          ))}
        </Stack>
      </Checkbox.Group>
    )
  },
)