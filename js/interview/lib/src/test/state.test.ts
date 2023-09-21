import { ObjectFieldState, createState } from "#src/field/state.js"
import { Schema } from "#src/types.js"

const schema1: Schema = {
  type: "object",
  properties: {
    field_0: {
      type: "string",
    },
    field_1: {
      type: "integer",
    },
    field_2: {
      type: "string",
      nullable: true,
    },
  },
  required: ["field_0", "field_1"],
}

test("field state can be created and assigned", () => {
  const state = createState(schema1) as ObjectFieldState

  expect(state.value).toBeNull()

  state.value = {
    field_0: "test",
    field_1: "test2",
    field_2: null,
  }

  expect(state.value).toEqual({
    field_0: "test",
    field_1: "test2",
    field_2: null,
  })

  expect(Object.keys(state.properties ?? {})).toEqual([
    "field_0",
    "field_1",
    "field_2",
  ])
})

test("field state is validated", () => {
  const state = createState(schema1) as ObjectFieldState

  expect(state.value).toBeNull()

  state.value = {
    field_0: "test",
    field_1: 1,
  }

  expect(state.errors).toEqual([])
  expect(state.isValid).toBe(true)

  state.value = {
    field_0: "test",
    field_1: "x",
  }

  expect(state.isValid).toBe(false)
  expect(state.properties?.field_0.isValid).toBe(true)
  expect(state.properties?.field_1.isValid).toBe(false)

  if (state.properties) {
    state.properties.field_1.value = 2
  }

  expect(state.isValid).toBe(true)
  expect(state.properties?.field_1.isValid).toBe(true)
})
