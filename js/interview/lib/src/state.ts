import { createSchema, isType } from "#src/schema/json-schema.js"
import { ErrorObj, JSONSchema } from "#src/types.js"
import { computed, makeAutoObservable, observable } from "mobx"

interface FieldState<T> {
  get schema(): JSONSchema

  get value(): T | null | undefined
  setValue(v: T | null | undefined): void

  get error(): string | undefined
  get isValid(): boolean

  get touched(): boolean
  setTouched(): void

  reset(): void
}

export interface ObjectFieldState extends FieldState<Record<string, unknown>> {
  readonly properties: Record<string, FieldState<unknown>> | null | undefined
}

type GetErrors = () => ErrorObj | undefined

class ScalarFieldState<T> implements FieldState<T> {
  value: T | null | undefined
  touched = false

  get error() {
    const obj = this.getErrors()
    if (obj?._errors && obj._errors.length > 0) {
      return obj._errors[0]
    } else {
      return undefined
    }
  }

  get isValid() {
    return this.error == null
  }

  constructor(
    public schema: JSONSchema,
    private getErrors: GetErrors,
    private initialValue?: T | null | undefined,
  ) {
    this.value = initialValue
    makeAutoObservable(this)
  }

  setValue(v: T | null | undefined) {
    this.value = v
  }

  setTouched() {
    this.touched = true
  }

  reset() {
    this.value = this.initialValue
    this.touched = false
  }
}

class ObjectFieldStateImpl implements FieldState<Record<string, unknown>> {
  public properties: Record<string, FieldState<unknown>> | null | undefined

  get value() {
    if (this.properties == null) {
      return this.properties
    }

    const obj: Record<string, unknown> = {}

    for (const [prop, state] of Object.entries(this.properties)) {
      if (state.value !== undefined) {
        obj[prop] = state.value
      }
    }

    return obj
  }

  get touched() {
    return Object.values(this.properties || {}).some((s) => s.touched)
  }

  get error() {
    const obj = this.getErrors()
    if (obj?._errors && obj._errors.length > 0) {
      return obj._errors[0]
    } else {
      return undefined
    }
  }

  get isValid() {
    return this.error == null
  }

  constructor(
    public schema: JSONSchema,
    private getErrors: GetErrors,
    private initialValue?: Record<string, unknown> | null | undefined,
  ) {
    this.setValue(initialValue)
    makeAutoObservable(this)
  }

  setValue(v: Record<string, unknown> | null | undefined) {
    if (v == null) {
      this.properties = v
      return
    }

    const properties = this.createProperties()

    for (const [prop, value] of Object.entries(v)) {
      properties[prop].setValue(value)
    }
  }

  setTouched() {
    for (const state of Object.values(this.properties ?? {})) {
      state.setTouched()
    }
  }

  private createProperties() {
    this.properties = {}

    for (const [prop, schema] of Object.entries(this.schema.properties || {})) {
      const getErrors = () => {
        const parentErr = this.getErrors()

        if (!parentErr) {
          return undefined
        }

        return parentErr[prop]
      }

      const initialValue = (this.initialValue ?? {})[prop]

      const state = _createState(
        schema,
        getErrors,
        getDefault(schema, initialValue),
      )
      this.properties[prop] = state
    }

    return this.properties
  }

  reset() {
    this.setValue(this.initialValue)
  }
}

const _createState = (
  schema: JSONSchema | boolean,
  getErrors: GetErrors,
  initialValue?: unknown,
): FieldState<unknown> => {
  if (typeof schema == "boolean") {
    return new ScalarFieldState({}, () => undefined)
  } else if (isType("object", schema)) {
    return new ObjectFieldStateImpl(
      schema,
      getErrors,
      getDefault(schema, initialValue) as Record<string, unknown>,
    )
  } else {
    return new ScalarFieldState(
      schema,
      getErrors,
      getDefault(schema, initialValue),
    )
  }
}

const getDefault = (schema: JSONSchema | boolean, initialValue?: unknown) => {
  if (typeof schema == "boolean") {
    return undefined
  } else if (isType("object", schema)) {
    const obj: Record<string, unknown> = {}
    const initObj: Record<string, unknown> = (initialValue ?? {}) as Record<
      string,
      unknown
    >

    for (const [prop, subschema] of Object.entries(schema.properties ?? {})) {
      obj[prop] = getDefault(subschema, initObj[prop])
    }

    return obj
  } else {
    return initialValue ?? schema.default
  }
}

/**
 * Create a {@link FieldState} for a schema.
 * @param schema - the schema
 * @param initialValue - the initial value
 * @returns the field state
 */
export const createState = (
  schema: JSONSchema,
  initialValue?: unknown,
): FieldState<unknown> => {
  const zodSchema = createSchema(schema)

  const stateBox = observable.box<FieldState<unknown> | null>(null)

  const validationResult = computed(() => {
    const state = stateBox.get()
    if (state == null) {
      return null
    }

    return zodSchema.safeParse(state.value)
  })

  const getErrors = computed(() => {
    const res = validationResult.get()
    if (!res || res.success) {
      return undefined
    } else {
      return res.error.format() as ErrorObj
    }
  })

  const state = _createState(schema, () => getErrors.get(), initialValue)
  stateBox.set(state)
  return state
}
