import { ObjectFieldState, createState } from "#src/state.js"
import { JSONSchema } from "#src/types.js"

const schema1: JSONSchema = {
  type: "string",
  default: "test",
  minLength: 2,
}

const schema2: JSONSchema = {
  type: "object",
  properties: {
    field_0: {
      type: ["string", "null"],
      minLength: 2,
    },
    field_1: {
      type: "integer",
    },
  },
  required: ["field_0"],
}

test("state creation works", () => {
  const state = createState(schema1)
  expect(state.value).toBe("test")
})

test("state creation sets initial value", () => {
  const state = createState(schema1, "other")
  expect(state.value).toBe("other")
})

test("state creation validates", () => {
  const state = createState(schema1)

  state.setValue("other")
  expect(state.value).toBe("other")
  expect(state.isValid).toBe(true)
  expect(state.error).toBeUndefined()

  state.setValue("x")
  expect(state.value).toBe("x")
  expect(state.isValid).toBe(false)
  expect(typeof state.error).toBe("string")
})

test("nested schemas work", () => {
  const state = createState(schema2)

  expect(state.value).toStrictEqual({})

  state.setValue({ field_0: "test", field_1: 1 })
  expect(state.value).toStrictEqual({ field_0: "test", field_1: 1 })

  state.setValue({ field_0: null })
  expect(state.value).toStrictEqual({ field_0: null })
})

test("values in subschemas work", () => {
  const state = createState(schema2) as ObjectFieldState
  const field_0 = state.properties?.field_0

  if (!field_0) return

  field_0.setValue("value")
  expect(field_0.value).toBe("value")
  expect(state.value).toStrictEqual({
    field_0: "value",
  })
})
