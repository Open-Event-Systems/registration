import { FieldProps } from "#src/types.js"
import {
  createStyles,
  DefaultProps,
  Selectors,
  TextInput,
  TextInputProps,
  useComponentDefaultProps,
} from "@mantine/core"
import { ScalarFieldState } from "@open-event-systems/interview-lib"
import { action } from "mobx"
import { observer } from "mobx-react-lite"

const useStyles = createStyles(() => ({ root: {} }))

export type TextFieldProps = FieldProps &
  DefaultProps<Selectors<typeof useStyles>> &
  Omit<
    TextInputProps,
    "name" | "error" | "value" | "onChange" | "onBlur" | "styles"
  >

/**
 * Component for a text field.
 */
export const TextField = observer((props: TextFieldProps) => {
  const { className, classNames, styles, unstyled, required, ...other } =
    useComponentDefaultProps("OESITextField", {}, props)
  const { cx, classes } = useStyles(undefined, {
    name: "OESITextField",
    classNames,
    styles,
    unstyled,
  })

  const state = props.state as ScalarFieldState

  const value = state.value != null ? state.value.toString() : ""
  const error = !state.isValid && state.touched
  const errorMessage = error ? state.errors[0].message : undefined
  const autoComplete = state.schema["x-autocomplete"] ?? undefined
  const inputMode = state.schema["x-input-mode"] ?? undefined

  return (
    <TextInput
      className={cx(className, classes.root)}
      label={state.schema.title || undefined}
      required={required}
      withAsterisk={required}
      autoComplete={autoComplete as TextFieldProps["autoComplete"]}
      inputMode={inputMode as TextFieldProps["inputMode"]}
      {...other}
      error={errorMessage}
      value={value}
      onChange={action((e) => {
        state.value = e.target.value
      })}
      onBlur={action(() => {
        state.touched = true
      })}
    />
  )
})

TextField.displayName = "TextField"
