import { createSchema } from "#src/schema/json-schema.js"
import { JSONSchema } from "#src/types.js"

const schema1: JSONSchema = {
  type: "string",
  minLength: 2,
  maxLength: 6,
}

const schema2: JSONSchema = {
  type: ["string", "null"],
  minLength: 2,
  maxLength: 6,
}

const schema3: JSONSchema = {
  type: "object",
  properties: {
    field_0: {
      type: ["string", "null"],
      "x-type": "text",
      minLength: 2,
      maxLength: 6,
    },
    field_1: {
      type: "number",
      "x-type": "number",
      minimum: 0,
      maximum: 10,
    },
    field_2: {
      "x-type": "select",
      oneOf: [
        {
          const: "1",
        },
        {
          const: "2",
        },
        {
          type: "null",
        },
      ],
    },
    field_3: {
      type: "array",
      "x-type": "select",
      maxItems: 2,
      items: {
        oneOf: [
          {
            const: "1",
          },
          {
            const: "2",
          },
          {
            const: "3",
          },
        ],
        uniqueItems: true,
      },
    },
  },
  required: ["field_1", "field_3"],
}

const selectSchema1: JSONSchema = {
  "x-type": "select",
  oneOf: [
    {
      const: "1",
    },
    {
      const: "2",
    },
    {
      type: "null",
    },
  ],
}

const selectSchema2: JSONSchema = {
  "x-type": "select",
  type: "array",
  items: {
    oneOf: [
      {
        const: "1",
      },
      {
        const: "2",
      },
      {
        const: "3",
      },
    ],
  },
  minItems: 1,
  maxItems: 2,
  uniqueItems: true,
}

const dateSchema1: JSONSchema = {
  type: "string",
  "x-type": "date",
  format: "date",
  "x-minimum": "2020-01-01",
  "x-maximum": "2020-12-31",
}

test("basic schema creation works", () => {
  const s = createSchema(schema1)

  const res = s.parse("test")
  expect(res).toEqual("test")
})

test("basic string validation works", () => {
  const s = createSchema(schema1)

  expect(() => s.parse("x")).toThrow()
  expect(() => s.parse("testtest")).toThrow()
})

test("strings are trimmed", () => {
  const s = createSchema(schema1)

  expect(s.parse("  test  ")).toEqual("test")
})

test("empty strings are coerced", () => {
  const s = createSchema(schema2)

  expect(s.parse("                ")).toBeNull()
})

test("complex schemas are parsed", () => {
  const s = createSchema(schema3)
  expect(
    s.parse({
      field_0: " test ",
      field_1: 5,
      field_2: "2",
      field_3: ["2", "3"],
    }),
  ).toStrictEqual({
    field_0: "test",
    field_1: 5,
    field_2: "2",
    field_3: ["2", "3"],
  })
})

test("complex schemas handle null", () => {
  const s = createSchema(schema3)
  expect(
    s.parse({
      field_0: "  ",
      field_1: 5,
      field_2: null,
      field_3: [],
    }),
  ).toStrictEqual({
    field_0: null,
    field_1: 5,
    field_2: null,
    field_3: [],
  })
})

test("selects validate inputs", () => {
  const s = createSchema(selectSchema1)
  expect(s.parse(null)).toBeNull()
  expect(s.parse("1")).toBe("1")
  expect(() => s.parse("3")).toThrow()
})

test("multi-selects validate inputs", () => {
  const s = createSchema(selectSchema2)
  expect(s.parse(["1", "3"])).toStrictEqual(["1", "3"])
  expect(() => s.parse(["1", "4"])).toThrow()
  expect(() => s.parse(["1", "2", "3"])).toThrow()
  expect(() => s.parse([])).toThrow()
  expect(() => s.parse(["1", "2", "1"])).toThrow()
})

test("date validation works", () => {
  const s = createSchema(dateSchema1)
  expect(s.parse("2020-07-04")).toBe("2020-07-04")
  expect(s.parse("2020-7-4")).toBe("2020-07-04")
  expect(() => s.parse("0000")).toThrow()
  expect(() => s.parse("00-02-28")).toThrow()
  expect(() => s.parse("2021-02-28")).toThrow()
})

test("date min/max validation works", () => {
  const s = createSchema(dateSchema1)
  expect(() => s.parse("2019-12-31")).toThrow()
  expect(() => s.parse("2021-01-01")).toThrow()
})
