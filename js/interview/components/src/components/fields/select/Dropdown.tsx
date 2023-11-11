import { getOptions, isNullable } from "#src/components/fields/select/util"
import { FieldProps } from "#src/types"
import { Select, SelectProps, useProps } from "@mantine/core"
import { observer } from "mobx-react-lite"

export type DropdownSelectFieldProps = FieldProps<string | string[]> &
  Omit<SelectProps, "data" | "value" | "onChange" | "error">

export const DropdownSelectField = observer(
  (props: DropdownSelectFieldProps) => {
    const { state, ...other } = useProps("OESIDropdownSelectField", {}, props)

    const options = getOptions(state.schema)
    const hasError = !state.isValid && state.touched
    const nullable = isNullable(state.schema)

    const value = Array.isArray(state.value) ? state.value[0] : state.value

    return (
      <Select
        classNames={{
          root: "OESIDropdownSelectField-root",
        }}
        label={state.schema.title}
        required={!nullable}
        withAsterisk={!nullable}
        clearable
        {...other}
        data={options}
        error={hasError ? state.error : undefined}
        value={value || null}
        onChange={(e) => {
          state.setValue(e)
          state.setTouched()
        }}
        onDropdownClose={() => {
          state.setTouched()
        }}
      />
    )
  },
)
