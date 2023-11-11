import { FieldProps } from "#src/types"
import { TextInput, TextInputProps, useProps } from "@mantine/core"
import { observer } from "mobx-react-lite"

export type TextFieldProps = FieldProps<string> &
  Omit<TextInputProps, "error" | "value" | "onChange" | "onBlur">

/**
 * Component for a text field.
 */
export const TextField = observer((props: TextFieldProps) => {
  const { state, ...other } = useProps("OESITextField", {}, props)

  const value = state.value
  const error = state.error
  const hasError = !state.isValid && state.touched
  const nullable = !!state.schema.type?.includes("null")

  return (
    <TextInput
      classNames={{
        root: "OESITextField-root",
      }}
      label={state.schema.title || undefined}
      required={!nullable}
      withAsterisk={!nullable}
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
