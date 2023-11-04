import {
  InterviewStateRecordImpl,
  makeInterviewRecordStore,
} from "#src/store.js"
import { IncompleteStateResponse } from "#src/types.js"

const response1: IncompleteStateResponse = {
  complete: false,
  content: null,
  state: "foo",
  update_url: "",
}

const response2: IncompleteStateResponse = {
  complete: false,
  content: null,
  state: "bar",
  update_url: "",
}

test("interview state generates IDs", () => {
  const s1 = new InterviewStateRecordImpl(response1, {}, {})
  const s2 = new InterviewStateRecordImpl(response2, {}, {})
  expect(s1.id).toBe("foo")
  expect(s2.id).toBe("bar")
})

test("state store loads records", () => {
  window.sessionStorage.setItem(
    "interview-state-v1",
    '[{"r": {"content": null, "state": "foo", "update_url": "x"}, "v": {"a": "b"}, "m": {"x": 1}}]',
  )
  const store = makeInterviewRecordStore()
  store.load()

  const record = store.getRecord("foo")
  expect(record?.id).toBe("foo")
  expect(record?.fieldValues).toStrictEqual({ a: "b" })
  expect(record?.stateResponse).toStrictEqual({
    state: "foo",
    content: null,
    update_url: "x",
  })
  expect(record?.metadata).toStrictEqual({ x: 1 })
})

test("state store saves records", () => {
  const store = makeInterviewRecordStore()
  const record = new InterviewStateRecordImpl(
    response2,
    { foo: "bar" },
    { x: 1 },
  )
  store.saveRecord(record)

  const loadedStore = makeInterviewRecordStore()
  loadedStore.load()

  const loadedRecord = loadedStore.getRecord("bar")
  expect(loadedRecord?.fieldValues).toStrictEqual({ foo: "bar" })
  expect(loadedRecord?.metadata).toStrictEqual({ x: 1 })
})
