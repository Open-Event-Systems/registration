import { useValue } from "#src/components/util.js"
import { FieldProps } from "#src/types.js"
import {
  createStyles,
  DefaultProps,
  Selectors,
  TextInput,
  TextInputProps,
  useComponentDefaultProps,
} from "@mantine/core"

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
export const TextField = (props: TextFieldProps) => {
  const {
    className,
    classNames,
    styles,
    unstyled,
    state,
    path,
    required,
    ...other
  } = useComponentDefaultProps("OESITextField", {}, props)
  const { cx, classes } = useStyles(undefined, {
    name: "OESITextField",
    classNames,
    styles,
    unstyled,
  })

  const [value, setValue] = useValue<string>(state, path)
  const error = state.getError(path)
  const errorMessage = error?._errors ? error._errors[0] : undefined
  const autoComplete = state.schema["x-autocomplete"]
  const inputMode = state.schema["x-input-mode"]

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
      value={value || ""}
      onChange={(e) => {
        setValue(e.target.value)
      }}
      // onBlur={action(() => {
      //   state.touched = true
      // })}
    />
  )
}
