import {
  ArraySchema,
  BooleanSchema,
  IntegerSchema,
  NumberSchema,
  ObjectSchema,
  Schema,
  SchemaTypeKeys,
  SchemaTypeMap,
  StringSchema,
} from "#src/types.js"
import { z } from "zod"

export const createZodSchema = (schema: Schema): z.ZodType<unknown> => {
  let typeSchemas: z.ZodType<unknown>[] = []

  if (isType(schema, "string")) {
    typeSchemas.push(createStringZodSchema(schema))
  }

  if (isType(schema, "number") || isType(schema, "integer")) {
    typeSchemas.push(createNumberZodSchema(schema))
  }

  if (isType(schema, "boolean")) {
    typeSchemas.push(createBooleanZodSchema(schema))
  }

  if (isType(schema, "object")) {
    typeSchemas.push(createObjectZodSchema(schema))
  }

  if (isType(schema, "array")) {
    typeSchemas.push(createArrayZodSchema(schema))
  }

  if (isType(schema, "null")) {
    typeSchemas.push(createNullZodSchema())
  }

  let zodSchema = typeSchemas.reduce((schema, prev) => prev.or(schema))

  if (isType(schema, "string")) {
    // when parsing a nullable string, coerce the empty string to null
    if (isType(schema, "null")) {
      zodSchema = z.preprocess(coerceNull, zodSchema)
    }

    // when parsing a string, trim it
    zodSchema = z.preprocess(trimStrings, zodSchema)
  }

  if (schema.const !== undefined) {
    zodSchema = zodSchema.and(createConstZodSchema(schema.const))
  }

  if (schema.oneOf !== undefined) {
    zodSchema = zodSchema.and(createOneOfZodSchema(schema.oneOf))
  }

  return zodSchema
}

const createObjectZodSchema = (
  schema: ObjectSchema,
): z.ZodType<Record<string, unknown>> => {
  const obj: Record<string, z.ZodTypeAny> = {}

  if (schema.properties === undefined) {
    return z.record(z.string(), z.unknown())
  }

  const required = schema.required ?? []

  for (const [prop, subschema] of Object.entries(schema.properties ?? {})) {
    const zs = createZodSchema(subschema)

    if (!required.includes(prop)) {
      obj[prop] = zs.optional()
    } else {
      obj[prop] = zs
    }
  }

  return z.object(obj, { invalid_type_error: "Invalid value" })
}

const createArrayZodSchema = (
  schema: ArraySchema,
): z.ZodArray<z.ZodType<unknown>> => {
  const itemSchema = schema.items ? createZodSchema(schema.items) : z.unknown()

  return z.array(itemSchema, { invalid_type_error: "Invalid value" })
}

const trimStrings = <T>(val: T): string | T => {
  if (typeof val == "string") {
    return val.trim()
  } else {
    return val
  }
}

const coerceNull = <T>(val: T): T | null => {
  if (val === "") {
    return null
  } else {
    return val
  }
}

const createStringZodSchema = (schema: StringSchema): z.ZodString => {
  let zs = z.string({ invalid_type_error: "Invalid value" })

  if (schema.minLength != null) {
    zs = zs.min(
      schema.minLength,
      `Must be at least ${schema.minLength} characters`,
    )
  }

  if (schema.maxLength != null) {
    zs = zs.max(
      schema.maxLength,
      `Must be at most ${schema.minLength} characters`,
    )
  }

  if (schema.pattern != null) {
    zs = zs.regex(new RegExp(schema.pattern), "Invalid value")
  }

  if (schema.format == "email") {
    // TODO: more validation
    zs = zs.email("Invalid email")
  }

  return zs
}

const createNumberZodSchema = (
  schema: NumberSchema | IntegerSchema,
): z.ZodNumber => {
  let zs = z.number({ invalid_type_error: "Invalid value" })

  if (schema.minimum != null) {
    zs = zs.min(schema.minimum, `Must be at least ${schema.minimum}`)
  }

  if (schema.maximum != null) {
    zs = zs.max(schema.maximum, `Must be at most ${schema.maximum}`)
  }

  if (isType(schema, "integer")) {
    zs = zs.int("Invalid value")
  }

  return zs
}

const createBooleanZodSchema = (schema: BooleanSchema): z.ZodBoolean => {
  return z.boolean({ invalid_type_error: "Invalid value" })
}

const createConstZodSchema = <T>(value: T): z.ZodType<T> => {
  // does not handle objects/arrays...
  return z.custom((val): val is T => val === value, {
    message: "Invalid value",
  })
}

const createOneOfZodSchema = (subSchemas: Schema[]): z.ZodType<unknown> => {
  return subSchemas
    .map((subschema) => createZodSchema(subschema))
    .reduce((subschema, prev) => prev.or(subschema))
}

const createNullZodSchema = (): z.ZodNull => z.null()

export const isType = <T extends SchemaTypeKeys>(
  schema: Schema,
  t: T,
): schema is SchemaTypeMap[T] => {
  return (
    !!schema.type &&
    (schema.type == t ||
      (Array.isArray(schema.type) && schema.type.includes(t)))
  )
}
