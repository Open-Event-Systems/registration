import { FieldProps } from "#src/types.js"
import { NumberInput, NumberInputProps, useProps } from "@mantine/core"
import { observer } from "mobx-react-lite"

export type NumberFieldProps = FieldProps<string> &
  Omit<NumberInputProps, "value" | "error" | "onChange" | "onBlur">

export const NumberField = observer((props: NumberFieldProps) => {
  const { state, required, ...other } = useProps("OESINumberField", {}, props)

  const error = state.error
  const hasError = !state.isValid && state.touched

  let value
  if (typeof state.value == "number") {
    value = state.value
  } else if (typeof state.value == "string") {
    if (state.value == "") {
      value = ""
    } else {
      const parsed = parseFloat(state.value)

      if (isNaN(parsed)) {
        value = state.value
      } else {
        value = parsed
      }
    }
  } else {
    value = ""
  }

  return (
    <NumberInput
      classNames={{
        root: "OESINumberField-root",
      }}
      label={state.schema.title || undefined}
      required={required}
      withAsterisk={required}
      autoComplete={state.schema["x-autocomplete"]}
      inputMode={state.schema["x-input-mode"] as NumberInputProps["inputMode"]}
      min={state.schema.minimum}
      max={state.schema.maximum}
      step={1}
      {...other}
      value={value}
      error={hasError ? error : undefined}
      onChange={(e) => {
        state.setValue(String(e))
      }}
    />
  )
})

NumberField.displayName = "NumberField"
