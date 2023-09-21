import {
  Checkbox,
  CheckboxGroupProps,
  createStyles,
  DefaultProps,
  Radio,
  RadioGroupProps,
  Select,
  Selectors,
  SelectProps,
  Stack,
  StackProps,
  useComponentDefaultProps,
} from "@mantine/core"
import { observer } from "mobx-react-lite"
import { FieldProps } from "#src/types.js"
import { action } from "mobx"
import { FieldState } from "@open-event-systems/interview-lib"

export type SelectFieldProps = FieldProps

/**
 * Renders the appropriate type of component for a select field.
 */
export const SelectField = observer((props: SelectFieldProps) => {
  const { state } = props

  const componentType = state.schema["x-component"] ?? "select"

  if (componentType == "radio") {
    return <RadioSelectField {...props} />
  } else if (componentType == "checkbox") {
    return <CheckboxSelectField {...props} />
  } else {
    return <DropdownSelectField {...props} />
  }
})

SelectField.displayName = "SelectField"

const selectStyles = createStyles({ root: {} })

export type DropdownSelectFieldProps = FieldProps &
  DefaultProps<Selectors<typeof selectStyles>> &
  Omit<SelectProps, "data" | "onChange" | "onBlur" | "value" | "styles">

/**
 * A dropdown select component.
 */
export const DropdownSelectField = observer(
  (props: DropdownSelectFieldProps) => {
    const {
      styles,
      className,
      classNames,
      unstyled,
      state,
      required,
      ...other
    } = useComponentDefaultProps("OESIDropdownSelectField", {}, props)

    const { classes, cx } = selectStyles(undefined, {
      name: "OESIDropdownSelectField",
      classNames,
      styles,
      unstyled,
    })

    const error =
      !state.isValid && state.touched ? state.errors[0].message : undefined

    return (
      <Select
        className={cx(className, classes.root)}
        label={state.schema.title}
        required={required || !state.schema.nullable}
        {...other}
        error={error}
        value={state.value != null ? `${state.value}` : null}
        onChange={action((e) => {
          state.value = e
        })}
        onDropdownClose={action(() => {
          state.touched = true
        })}
        data={getOptions(state)}
        autoComplete={
          state.schema["x-autocomplete"] as SelectProps["autoComplete"]
        }
      />
    )
  },
)

DropdownSelectField.displayName = "DropdownSelectField"

const radioStyles = createStyles({
  root: {},
  radio: {},
})

export type RadioSelectFieldProps = FieldProps & {
  StackProps?: Partial<StackProps>
} & DefaultProps<Selectors<typeof radioStyles>> &
  Omit<RadioGroupProps, "children" | "value" | "onChange" | "onBlur">

/**
 * A radio button group select component.
 */
export const RadioSelectField = observer((props: RadioSelectFieldProps) => {
  const {
    className,
    classNames,
    styles,
    unstyled,
    StackProps,
    state,
    required,
    ...other
  } = useComponentDefaultProps("OESIRadioSelectField", {}, props)

  const { classes, cx } = radioStyles(undefined, {
    name: "OESIRadioSelectField",
    classNames,
    styles,
    unstyled,
  })

  const error =
    !state.isValid && state.touched ? state.errors[0].message : undefined

  return (
    <Radio.Group
      label={state.schema.title}
      withAsterisk={required || !state.schema.nullable}
      className={cx(className, classes.root)}
      {...other}
      error={error}
      value={state.value as string | undefined}
      onChange={action((e) => {
        state.value = e
      })}
      onBlur={action(() => {
        state.touched = true
      })}
      styles={(theme) => ({
        error: {
          paddingTop: theme.spacing.xs,
        },
      })}
    >
      <Stack spacing="sm" {...StackProps}>
        {getOptions(state).map((opt) => (
          <Radio
            className={classes.radio}
            key={opt.value}
            value={opt.value}
            label={opt.label}
          />
        ))}
      </Stack>
    </Radio.Group>
  )
})

RadioSelectField.displayName = "RadioSelectField"

const checkboxStyles = createStyles({
  root: {},
  checkbox: {},
})

export type CheckboxSelectFieldProps = FieldProps & {
  StackProps?: Partial<StackProps>
} & DefaultProps<Selectors<typeof checkboxStyles>> &
  Omit<CheckboxGroupProps, "children" | "value" | "onChange" | "onBlur">

/**
 * A checkbox group select component.
 */
export const CheckboxSelectField = observer(
  (props: CheckboxSelectFieldProps) => {
    const {
      className,
      classNames,
      styles,
      unstyled,
      StackProps,
      state,
      required,
      ...other
    } = useComponentDefaultProps("OESICheckboxSelectField", {}, props)

    const { classes, cx } = checkboxStyles(undefined, {
      name: "OESICheckboxSelectField",
      classNames,
      styles,
      unstyled,
    })

    const error =
      !state.isValid && state.touched ? state.errors[0].message : undefined

    const isMulti = state.schema.type == "array"

    const value = isMulti ? state.value ?? [] : state.value ? [state.value] : []

    return (
      <Checkbox.Group
        label={state.schema.title}
        withAsterisk={required || !state.schema.nullable}
        className={cx(className, classes.root)}
        {...other}
        error={error}
        value={value as string[]}
        onChange={action((e) => {
          if (state.schema.type == "array") {
            state.value = e
          } else {
            if (e.length == 0) {
              state.value = null
            } else {
              state.value = e[0]
            }
          }
        })}
        onBlur={action(() => {
          state.touched = true
        })}
        styles={(theme) => ({
          error: {
            paddingTop: theme.spacing.xs,
          },
        })}
      >
        <Stack spacing="sm" {...StackProps}>
          {getOptions(state).map((opt) => (
            <Checkbox
              className={classes.checkbox}
              key={opt.value}
              value={opt.value}
              label={opt.label}
            />
          ))}
        </Stack>
      </Checkbox.Group>
    )
  },
)

CheckboxSelectField.displayName = "CheckboxSelectField"

/**
 * Get the option labels from the json schema.
 */
const getOptions = (state: FieldState) => {
  if (state.schema.type == "array") {
    return (
      state.schema.items?.oneOf?.map((opt, i) => ({
        label: opt.title,
        value: (opt.const as string) || `${i + 1}`,
      })) ?? []
    )
  } else {
    return (
      state.schema.oneOf
        ?.filter((opt) => opt.type != "null")
        .map((opt, i) => ({
          label: opt.title,
          value: (opt.const as string) || `${i + 1}`,
        })) ?? []
    )
  }
}
