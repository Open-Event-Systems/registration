import { FieldProps } from "#src/types"
import { useProps } from "@mantine/core"
import { DateInput, DateInputProps } from "@mantine/dates"
import dayjs from "dayjs"
import { observer } from "mobx-react-lite"

export type DateFieldProps = FieldProps<string> &
  Omit<DateInputProps, "value" | "onChange" | "error">

export const DateField = observer((props: DateFieldProps) => {
  const { state, ...other } = useProps("OESIDateField", {}, props)

  const hasError = !state.isValid && state.touched
  const nullable = !!state.schema.type?.includes("null")

  let value = null

  if (state.value) {
    const parsed = dayjs(state.value)
    if (parsed.isValid()) {
      value = parsed.toDate()
    }
  }

  return (
    <DateInput
      classNames={{
        root: "OESIDateField-root",
      }}
      label={state.schema.title}
      required={!nullable}
      withAsterisk={!nullable}
      inputMode={state.schema["x-input-mode"] as DateFieldProps["inputMode"]}
      autoComplete={state.schema["x-autocomplete"]}
      {...other}
      value={value}
      error={hasError ? state.error : undefined}
      onChange={(e) => {
        if (e) {
          state.setValue(dayjs(e).format("YYYY-MM-DD"))
        } else {
          state.setValue(null)
        }
      }}
      onBlur={() => {
        state.setTouched()
      }}
    />
  )
})

DateField.displayName = "DateField"
