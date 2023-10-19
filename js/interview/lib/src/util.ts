import { Schema } from "#src/types.js"

type OptionalType = {
  type: (
    | "string"
    | "number"
    | "integer"
    | "object"
    | "array"
    | "boolean"
    | "null"
  )[]
}

/**
 * Get whether the schema is for an optional field.
 */
export const isOptional = (schema: Schema): schema is OptionalType => {
  return Array.isArray(schema.type) && schema.type.includes("null")
}
