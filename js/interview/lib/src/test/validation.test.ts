import { createValidator } from "#src/field/validation.js"
import { Schema } from "#src/types.js"

const schema1: Schema = {
  type: "object",
  properties: {
    field_0: {
      type: "string",
      minLength: 2,
      maxLength: 20,
    },
    field_1: {
      type: "string",
      minLength: 2,
      maxLength: 20,
      nullable: true,
    },
  },
  required: ["field_0"],
}

const boolSchema: Schema = {
  type: "object",
  properties: {
    field_0: {
      type: "string",
      "x-type": "select",
      "x-component": "checkbox",
      oneOf: [
        { type: "null" },
        {
          const: "1",
          title: "Enable",
        },
      ],
      nullable: true,
    },
  },
  required: [],
}

test("schemas validate inputs", () => {
  const validator = createValidator(schema1)

  const input1 = { field_0: "test" }
  const input2 = { field_0: "test", field_2: "test2" }
  const input3 = { field_0: "test", field_2: null }
  const input4 = { field_0: "test", field_2: undefined }

  expect(validator(input1).errors).toEqual([])
  expect(validator(input2).errors).toEqual([])
  expect(validator(input3).errors).toEqual([])
  expect(validator(input4).errors).toEqual([])
})

test("schemas return validation errors", () => {
  const validator = createValidator(schema1)

  const input1 = {}
  const input2 = { field_0: "a" }
  const input3 = { field_0: "abc", field_1: "a" }

  expect(validator(input1).errors.length).toBeGreaterThan(0)
  expect(validator(input2).errors.length).toBeGreaterThan(0)
  expect(validator(input3).errors.length).toBeGreaterThan(0)
})

test("optional select schema works", () => {
  const validator = createValidator(boolSchema)

  expect(validator({ field_0: "1" }).errors.length).toBe(0)
  expect(validator({}).errors.length).toBe(0)
  expect(validator({ field_0: null }).errors.length).toBe(0)
})
