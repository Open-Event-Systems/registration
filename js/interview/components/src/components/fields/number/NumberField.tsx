import { FieldProps } from "#src/types"
import { NumberInput, NumberInputProps, useProps } from "@mantine/core"
import { observer } from "mobx-react-lite"

export type NumberFieldProps = FieldProps<string | number> &
  Omit<NumberInputProps, "value" | "error" | "onChange" | "onBlur">

export const NumberField = observer((props: NumberFieldProps) => {
  const { state, ...other } = useProps("OESINumberField", {}, props)

  const error = state.error
  const hasError = !state.isValid && state.touched
  const nullable = !!state.schema.type?.includes("null")

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
      required={!nullable}
      withAsterisk={!nullable}
      autoComplete={state.schema["x-autocomplete"]}
      inputMode={state.schema["x-input-mode"] as NumberInputProps["inputMode"]}
      min={state.schema.minimum}
      max={state.schema.maximum}
      step={1}
      {...other}
      value={value}
      error={hasError ? error?.message : undefined}
      onChange={(e) => {
        if (typeof e == "string") {
          const trimmed = e.trim()
          if (trimmed == "") {
            state.setValue(null)
          } else {
            state.setValue(trimmed)
          }
        } else {
          state.setValue(e)
        }
      }}
      onBlur={() => {
        state.setTouched()
      }}
    />
  )
})

NumberField.displayName = "NumberField"
