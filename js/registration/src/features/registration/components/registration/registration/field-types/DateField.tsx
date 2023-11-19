import { createField } from "#src/features/registration/components/registration/registration/field-types/Base"
import { Text } from "@mantine/core"
import { DateInput, DateTimePicker } from "@mantine/dates"
import dayjs from "dayjs"

export const DateTimeField = createField<string>(
  ({ label, value, setValue }) => {
    const parsed = value ? dayjs(value) : undefined
    let displayValue
    if (parsed && parsed.isValid()) {
      displayValue = parsed.toDate()
    }

    return (
      <DateTimePicker
        aria-label={label}
        value={displayValue}
        onChange={(v) => {
          if (v != null) {
            setValue(dayjs(v).toISOString())
          } else {
            setValue(undefined)
          }
        }}
      />
    )
  },
  ({ value }) => {
    const parsed = dayjs(value)
    let displayValue
    if (parsed.isValid()) {
      displayValue = parsed.format("YYYY-MM-DD HH:mm:ss Z")
    } else {
      displayValue = value
    }

    return <Text>{displayValue}</Text>
  },
)

export const DateField = createField<string>(
  ({ label, value, setValue }) => {
    const parsed = value ? dayjs(value) : undefined
    let displayValue
    if (parsed && parsed.isValid()) {
      displayValue = parsed.toDate()
    }

    return (
      <DateInput
        aria-label={label}
        value={displayValue}
        onChange={(v) => {
          if (v != null) {
            setValue(dayjs(v).toISOString())
          } else {
            setValue(undefined)
          }
        }}
      />
    )
  },
  ({ value }) => {
    const parsed = dayjs(value)
    let displayValue
    if (parsed.isValid()) {
      displayValue = parsed.format("YYYY-MM-DD")
    } else {
      displayValue = value
    }

    return <Text>{displayValue}</Text>
  },
)
