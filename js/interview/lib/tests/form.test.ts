import { createFormState } from "#src/form.js"
import { JSONSchema } from "#src/types.js"

const schema1: JSONSchema = {
  type: "object",
  properties: {
    field_0: {
      type: "string",
      default: "default",
    },
    field_1: {
      type: ["number", "null"],
      default: null,
    },
    field_2: {
      type: ["number"],
    },
  },
  required: ["field_0", "field_1"],
}

test("schema state is created correctly", () => {
  const state = createFormState(schema1)
  expect(state.getValue()).toStrictEqual({
    field_0: "default",
    field_1: null,
  })
})

test("schema state getValue works", () => {
  const state = createFormState(schema1)

  expect(state.getValue(["field_0"])).toBe("default")
  expect(state.getValue(["field_1"])).toBeNull()
  expect(state.getValue(["field_2"])).toBeUndefined()
  expect(state.getValue(["missing"])).toBeUndefined()
})

test("schema state setValue works", () => {
  const state = createFormState(schema1)
  state.setValue(["field_0"], "test")
  state.setValue(["field_2"], 1)

  expect(state.getValue()).toStrictEqual({
    field_0: "test",
    field_1: null,
    field_2: 1,
  })
})

test("schema state error handling works", () => {
  const state = createFormState(schema1)
  state.setValue(["field_0"], 123)

  expect(state.getError(["field_0"])?._errors?.length).toBe(1)
})
