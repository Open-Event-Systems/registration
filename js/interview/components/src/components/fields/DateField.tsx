import {
  createStyles,
  DefaultProps,
  Selectors,
  useComponentDefaultProps,
} from "@mantine/core"
import { observer } from "mobx-react-lite"
import { DateInput, DateInputProps } from "@mantine/dates"
import dayjs, { Dayjs, isDayjs } from "dayjs"
import { FieldProps } from "#src/types.js"
import { action } from "mobx"

const useStyles = createStyles(() => ({ root: {} }))

export type DateFieldProps = FieldProps &
  DefaultProps<Selectors<typeof useStyles>> &
  Omit<
    DateInputProps,
    "name" | "error" | "value" | "onChange" | "onBlur" | "styles"
  >

/**
 * Component for a date field.
 */
export const DateField = observer((props: DateFieldProps) => {
  const { className, classNames, styles, unstyled, state, required, ...other } =
    useComponentDefaultProps("OESIDateField", {}, props)
  const { cx, classes } = useStyles(undefined, {
    name: "OESIDateField",
    classNames,
    styles,
    unstyled,
  })

  let value
  if (
    typeof state.value == "string" ||
    state.value instanceof Date ||
    isDayjs(state.value)
  ) {
    value = parseDate(state.value)
  } else {
    value = null
  }

  const errorMessage =
    !state.isValid && state.touched ? state.errors[0].message : undefined

  return (
    <DateInput
      className={cx(classes.root, className)}
      popoverProps={{
        withinPortal: true,
      }}
      size="xs"
      label={state.schema.title}
      required={required || !state.schema.nullable}
      withAsterisk={required || !state.schema.nullable}
      autoComplete={
        state.schema["x-autocomplete"] as DateFieldProps["autoComplete"]
      }
      inputMode="numeric"
      weekendDays={[]}
      {...other}
      error={errorMessage}
      value={value}
      onChange={action((e) => {
        if (e) {
          state.value = dayjs(e).format("YYYY-MM-DD")
        } else {
          state.value = null
        }
      })}
      onBlur={action(() => {
        state.touched = true
      })}
    />
  )
})

DateField.displayName = "DateField"

const parseDate = (obj: string | Date | Dayjs): Date | null => {
  const parsed = dayjs(obj)
  return parsed.isValid() ? parsed.toDate() : null
}
