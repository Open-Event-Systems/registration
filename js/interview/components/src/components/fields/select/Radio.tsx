import { getOptions } from "#src/components/fields/select/util.js"
import { FieldProps } from "#src/types.js"
import { Radio, RadioGroupProps, RadioProps, Stack } from "@mantine/core"
import { observer } from "mobx-react-lite"

import "./Radio.module.css"

export type RadioSelectFieldProps = FieldProps<string | string[]> &
  Omit<RadioGroupProps, "error" | "value" | "onChange" | "children"> & {
    RadioProps?: Partial<RadioProps>
  }

export const RadioSelectField = observer((props: RadioSelectFieldProps) => {
  const { state, required, RadioProps, ...other } = props

  const options = getOptions(state.schema)
  const hasError = !state.isValid && state.touched

  const value = Array.isArray(state.value) ? state.value[0] : state.value

  return (
    <Radio.Group
      classNames={{
        root: "OESIRadioSelectField-root",
      }}
      required={required}
      withAsterisk={required}
      label={state.schema.title}
      {...other}
      error={hasError ? state.error : undefined}
      value={value || undefined}
      onChange={(e) => {
        state.setValue(e)
        state.setTouched()
      }}
    >
      <Stack
        classNames={{
          root: "OESIRadioSelectField-group",
        }}
      >
        {options.map((opt) => (
          <Radio
            key={opt.value}
            classNames={{
              root: "OESIRadioSelectField-radio-root",
            }}
            value={opt.value}
            {...RadioProps}
            label={opt.label}
          />
        ))}
      </Stack>
    </Radio.Group>
  )
})
