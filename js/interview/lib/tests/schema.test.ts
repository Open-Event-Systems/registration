import { createZodSchema } from "#src/schema.js"
import { Schema } from "#src/types.js"

const schema1: Schema = {
  type: "object",
  properties: {
    field_0: {
      type: "string",
      minLength: 2,
      maxLength: 10,
    },
    field_1: {
      type: "integer",
      minimum: 1,
      maximum: 10,
    },
  },
  required: ["field_0"],
}

test("zod schema parses", () => {
  const parsed = createZodSchema(schema1)

  const data = {
    field_0: "test",
    field_1: 2,
  }

  const result = parsed.safeParse(data)
  expect(result.success).toBe(true)
  if (result.success) {
    expect(result.data).toStrictEqual({ field_0: "test", field_1: 2 })
  }
})

test("zod schema validates", () => {
  const parsed = createZodSchema(schema1)

  const result1 = parsed.safeParse({ field_0: "x" })
  const result2 = parsed.safeParse({ field_0: "test", field_1: 0 })
  const result3 = parsed.safeParse({ field_1: 5 })

  expect(result1.success).toBe(false)
  expect(result2.success).toBe(false)
  expect(result3.success).toBe(false)
})

test("zod string schema trims strings", () => {
  const parsed = createZodSchema(schema1)

  const result = parsed.safeParse({ field_0: "  test " })

  expect(result.success).toBe(true)
  if (result.success) {
    expect(result.data).toStrictEqual({ field_0: "test" })
  }
})

test("zod string schema coerces empty strings", () => {
  const parsed = createZodSchema({
    type: "object",
    properties: {
      field_0: {
        type: ["string", "null"],
      },
    },
  })

  const result = parsed.safeParse({ field_0: "    " })

  expect(result.success).toBe(true)
  if (result.success) {
    expect(result.data).toStrictEqual({ field_0: null })
  }
})
