import { JSONSchema } from "@open-event-systems/interview-lib"

export const getOptions = (
  schema: JSONSchema,
): { value: string; label: string; primary: boolean; default: boolean }[] => {
  if (typeof schema != "object" || !schema) {
    return []
  }

  const options: {
    value: string
    label: string
    primary: boolean
    default: boolean
  }[] = []

  if (schema.items) {
    if (Array.isArray(schema.items)) {
      for (const entry of schema.items) {
        options.push(...getOptions(entry))
      }
    } else {
      options.push(...getOptions(schema.items))
    }

    const defaults = Array.isArray(schema.default) ? schema.default : []

    return options.map((opt) => ({
      ...opt,
      default: defaults.includes(opt.value),
    }))
  } else if (schema.oneOf) {
    for (const option of schema.oneOf) {
      if (typeof option == "object" && option.const) {
        const isDefault = schema.default === option.const
        options.push({
          value: String(option.const),
          label: option.title || String(option.const),
          default: isDefault,
          primary: !!option["x-primary"],
        })
      }
    }

    return options
  } else {
    return options
  }
}

export const isNullable = (schema: JSONSchema): boolean => {
  if (typeof schema != "object") {
    return false
  } else if (schema.items) {
    return schema.minItems == undefined || schema.minItems == 0
  } else if (schema.oneOf) {
    return !!schema.oneOf.find((o) => typeof o == "object" && o.type == "null")
  } else {
    return false
  }
}
