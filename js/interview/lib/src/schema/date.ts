/**
 * Date validation functions.
 * @module
 */

import { JSONSchema } from "#src/types.js"
import dayjs, { Dayjs, isDayjs } from "dayjs"
import { z } from "zod"

/**
 * Handle dates.
 */
export const handleDate = (
  zodSchema: z.ZodType<string>,
  schema: JSONSchema,
): z.ZodType<string> => {
  let zs = zodSchema
  zs = zs.transform((v, ctx) => {
    const date = parseDate(v)
    if (!date) {
      ctx.addIssue({
        code: "invalid_date",
        message: "Invalid date",
      })
      return v
    } else {
      return date.format("YYYY-MM-DD")
    }
  })

  if (schema["x-minimum"]) {
    const minDate = parseDate(schema["x-minimum"])
    if (minDate) {
      zs = zs.refine(
        (v) => {
          const date = parseDate(v)
          return date == null || !date.isBefore(minDate)
        },
        { message: "Choose a later date" },
      )
    }
  }

  if (schema["x-maximum"]) {
    const maxDate = parseDate(schema["x-maximum"])
    if (maxDate) {
      zs = zs.refine(
        (v) => {
          const date = parseDate(v)
          return date == null || !date.isAfter(maxDate)
        },
        { message: "Choose an earlier date" },
      )
    }
  }

  return zs
}

/**
 * Parse a date string.
 */
const parseDate = (v: unknown): Dayjs | null => {
  if (typeof v == "string") {
    const d = dayjs(v, "YYYY-MM-DD")
    if (d.isValid()) {
      return d
    } else {
      return null
    }
  } else if (isDayjs(v)) {
    return v
  } else if (v instanceof Date) {
    return dayjs(v)
  } else {
    return null
  }
}
