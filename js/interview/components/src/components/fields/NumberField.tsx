import {
  createStyles,
  DefaultProps,
  NumberInput,
  NumberInputProps,
  Selectors,
  useComponentDefaultProps,
} from "@mantine/core"
import { observer } from "mobx-react-lite"
import { FieldProps } from "#src/types.js"
import { action } from "mobx"

const numberFieldStyles = createStyles({ root: {} })

export type NumberFieldProps = FieldProps &
  DefaultProps<Selectors<typeof numberFieldStyles>> &
  Omit<NumberInputProps, "value" | "onChange" | "onBlur" | "styles">

/**
 * The component for a number field.
 */
export const NumberField = observer((props: NumberFieldProps) => {
  const { className, classNames, styles, unstyled, state, required, ...other } =
    useComponentDefaultProps("OESINumberField", {}, props)

  const { cx, classes } = numberFieldStyles(undefined, {
    name: "OESINumberField",
    classNames,
    styles,
    unstyled,
  })

  let value
  if (typeof state.value == "number") {
    value = state.value
  } else if (typeof state.value == "string") {
    const parsed = parseInt(state.value)
    value = isNaN(parsed) ? undefined : parsed
  }

  const errorMessage =
    !state.isValid && state.touched ? state.errors[0].message : undefined
  const autoComplete = state.schema["x-autocomplete"]
  const inputMode = state.schema["x-input-mode"]

  return (
    <NumberInput
      className={cx(className, classes.root)}
      label={state.schema.title}
      required={required || !!state.schema.nullable}
      withAsterisk={required || !!state.schema.nullable}
      autoComplete={autoComplete as NumberFieldProps["autoComplete"]}
      inputMode={inputMode as NumberFieldProps["inputMode"]}
      {...other}
      error={errorMessage}
      value={value}
      onChange={action((e) => {
        state.value = e == "" ? null : e
      })}
      onBlur={action(() => {
        state.touched = true
      })}
    />
  )
})

NumberField.displayName = "NumberField"
