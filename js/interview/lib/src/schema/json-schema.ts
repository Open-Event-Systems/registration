/**
 * JSON schema to Zod schema functions.
 *
 * @module
 */

import { handleDate } from "#src/schema/date.js"
import { JSONSchema } from "#src/types.js"
import { z } from "zod"

type SchemaTypeName = Extract<JSONSchema["type"], string>

/**
 * Create a Zod schema from a JSON schema.
 */
export const createSchema = (
  schema: JSONSchema | boolean,
): z.ZodType<unknown> => {
  if (typeof schema == "boolean") {
    return schema ? z.unknown() : z.never()
  }

  let schemas: z.ZodType<unknown>[] = []

  if (isType("string", schema)) {
    schemas.push(handleString(schema))
  }

  if (isType("number", schema) || isType("integer", schema)) {
    schemas.push(handleNumber(schema))
  }

  if (isType("boolean", schema)) {
    schemas.push(handleBoolean(schema))
  }

  if (isType("array", schema)) {
    schemas.push(handleArray(schema))
  }

  if (isType("object", schema)) {
    schemas.push(handleObject(schema))
  }

  if (isType("null", schema)) {
    schemas.push(handleNull(schema))
  }

  let zs = schemas.length > 0 ? schemas.reduce((s, p) => p.or(s)) : z.unknown()

  if (isType("string", schema)) {
    if (isType("null", schema)) {
      // coerce empty string to null
      zs = z.preprocess(coerceEmptyStrings, zs)
    }

    // trim strings
    zs = z.preprocess(trimStrings, zs)
  }

  // other constraints
  if (schema.const !== undefined) {
    // only handles primitives...
    zs = zs.refine((v) => v === schema.const, "Invalid value")
  }

  if (schema.oneOf !== undefined) {
    const subschemas =
      schema.oneOf.length > 0
        ? schema.oneOf.map((s) => createSchema(s)).reduce((s, p) => p.or(s))
        : z.never()
    zs = zs.and(subschemas)
  }

  return zs
}

/**
 * Array schema.
 */
const handleArray = (schema: JSONSchema): z.ZodType<unknown[]> => {
  let itemsSchema: z.ZodType<unknown>

  if (schema.items != null) {
    if (Array.isArray(schema.items)) {
      itemsSchema =
        schema.items.length > 0
          ? schema.items.map((s) => createSchema(s)).reduce((s, p) => p.and(s))
          : z.never()
    } else {
      itemsSchema = createSchema(schema.items)
    }
  } else {
    itemsSchema = z.unknown()
  }

  let zs = z.array(itemsSchema)

  if (schema.minItems != null) {
    zs = zs.min(schema.minItems)
  }

  if (schema.maxItems != null) {
    zs = zs.max(schema.maxItems)
  }

  let ze

  if (schema.uniqueItems) {
    ze = zs.refine(
      (v) => {
        const valSet = new Set(v)
        return valSet.size == v.length
      },
      { message: "Values must be unique" },
    )
  }

  return ze ?? zs
}

/**
 * Object schema.
 * @returns
 */
const handleObject = (
  schema: JSONSchema,
): z.ZodType<Record<string, unknown>> => {
  if (schema.properties == null) {
    return z.record(z.string(), z.unknown())
  }

  let obj: Record<string, z.ZodType<unknown>> = {}
  const required = schema.required || []

  for (const [prop, subschema] of Object.entries(schema.properties)) {
    const subz = createSchema(subschema)
    if (required) {
      obj[prop] = subz
    } else {
      obj[prop] = z.optional(subz)
    }
  }

  let zs = z.object(obj)

  return zs
}

/**
 * String schema.
 */
const handleString = (schema: JSONSchema): z.ZodType<string> => {
  let zs = z.string()

  if (schema.minLength != null) {
    zs = zs.min(schema.minLength)
  }

  if (schema.maxLength != null) {
    zs = zs.max(schema.maxLength)
  }

  if (schema.pattern != null) {
    const regexp = new RegExp(schema.pattern)
    zs = zs.regex(regexp)
  }

  let ze: z.ZodType<string>

  switch (schema.format) {
    case "email":
      // TODO: more email validation
      ze = zs.email()
      break
    case "date":
      ze = handleDate(zs, schema)
      break
    default:
      ze = zs
  }

  return ze
}

const trimStrings = (v: unknown): unknown => {
  if (typeof v == "string") {
    return v.trim()
  } else {
    return v
  }
}

const coerceEmptyStrings = (v: unknown): unknown => {
  if (v === "") {
    return null
  } else {
    return v
  }
}

/**
 * Number schema.
 */
const handleNumber = (schema: JSONSchema): z.ZodNumber => {
  let zs = z.number()

  if (schema.minimum != null) {
    zs = zs.min(schema.minimum)
  }

  if (schema.maximum != null) {
    zs = zs.max(schema.maximum)
  }

  if (isType("integer", schema)) {
    zs = zs.int()
  }

  return zs
}

/**
 * Boolean schema.
 */
const handleBoolean = (schema: JSONSchema): z.ZodBoolean => {
  return z.boolean()
}

/**
 * Null schema.
 */
const handleNull = (schema: JSONSchema): z.ZodNull => {
  return z.null()
}

/**
 * Return whether the schema includes a given type.
 */
const isType = <T extends SchemaTypeName>(
  t: T,
  schema: JSONSchema,
): schema is JSONSchema & { type: T } => {
  return (
    !!schema.type &&
    (schema.type === t ||
      (Array.isArray(schema.type) && schema.type.includes(t)))
  )
}
