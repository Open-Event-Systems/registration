import { FieldProps } from "#src/types.js"
import { TextInput, TextInputProps, useProps } from "@mantine/core"
import { observer } from "mobx-react-lite"

export type TextFieldProps = FieldProps<string> &
  Omit<TextInputProps, "error" | "value" | "onChange" | "onBlur">

/**
 * Component for a text field.
 */
export const TextField = observer((props: TextFieldProps) => {
  const { state, required, ...other } = useProps("OESITextField", {}, props)

  const value = state.value
  const error = state.error
  const hasError = !state.isValid && state.touched

  return (
    <TextInput
      classNames={{
        root: "OESITextField-root",
      }}
      label={state.schema.title || undefined}
      required={required}
      withAsterisk={required}
      autoComplete={
        state.schema["x-autocomplete"] as TextFieldProps["autoComplete"]
      }
      inputMode={state.schema["x-input-mode"] as TextFieldProps["inputMode"]}
      {...other}
      error={hasError ? error : undefined}
      value={value || ""}
      onChange={(e) => {
        state.setValue(e.target.value)
      }}
      onBlur={() => {
        state.setTouched()
      }}
    />
  )
})

TextField.displayName = "TextField"
