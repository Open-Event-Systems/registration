import { JSONSchema } from "@open-event-systems/interview-lib"

export const getOptions = (
  schema: JSONSchema,
): { value: string; label: string }[] => {
  if (typeof schema != "object" || !schema) {
    return []
  }

  const options: { value: string; label: string }[] = []

  if (schema.items) {
    if (Array.isArray(schema.items)) {
      for (const entry of schema.items) {
        options.push(...getOptions(entry))
      }
      return options
    } else {
      return getOptions(schema.items)
    }
  } else if (schema.oneOf) {
    for (const option of schema.oneOf) {
      if (typeof option == "object" && option.const) {
        options.push({
          value: String(option.const),
          label: option.title || String(option.const),
        })
      }
    }

    return options
  } else {
    return options
  }
}
