import { createSchema, isType } from "#src/schema/json-schema.js"
import {
  FieldState,
  JSONSchema,
  JSONSchemaOf,
  ObjectFieldState,
} from "#src/types.js"
import { JSONSchema7 } from "json-schema"
import { computed, makeAutoObservable, observable, toJS } from "mobx"

type ErrorObj = {
  [key in string]?: ErrorObj
} & { _errors?: string[] }

type GetErrors = () => ErrorObj | undefined

/**
 * Normal field state.
 */
class ScalarFieldState<T> implements FieldState<T> {
  value: T | null
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
    public schema: JSONSchema7,
    private getErrors: GetErrors,
    private initialValue?: T | null,
  ) {
    const defaultValue =
      typeof schema != "boolean" ? (schema.default as T) : undefined
    this.value =
      initialValue !== undefined ? initialValue : defaultValue ?? null
    makeAutoObservable(this)
  }

  setValue(v: T | null) {
    this.value = v
  }

  setTouched() {
    this.touched = true
  }

  reset() {
    const defaultValue =
      typeof this.schema != "boolean" ? (this.schema.default as T) : undefined
    this.value =
      this.initialValue !== undefined ? this.initialValue : defaultValue ?? null
    this.touched = false
  }
}

/**
 * Field state for an object. Maps property names to sub-{@link FieldState} instances.
 */
class ObjectFieldStateImpl implements ObjectFieldState {
  public properties: Record<string, FieldState<unknown> | undefined> | null =
    null

  /**
   * Map property names to the values of the sub-fields.
   */
  get value() {
    if (this.properties == null) {
      return this.properties
    }

    const obj: Record<string, unknown> = {}

    for (const [prop, state] of Object.entries(this.properties)) {
      if (state && state.value !== undefined) {
        obj[prop] = state.value
      }
    }

    return obj
  }

  get touched() {
    return Object.values(this.properties ?? {}).some((s) => !!s && s.touched)
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
    public schema: JSONSchemaOf<"object">,
    private getErrors: GetErrors,
    private initialValue?: Record<string, unknown> | null,
  ) {
    this.setValue(initialValue !== undefined ? initialValue : {})

    makeAutoObservable(this)
  }

  setValue(v: Record<string, unknown> | null) {
    if (v == null) {
      this.properties = v
      return
    }

    const properties = this.createObject(this.schema, this.initialValue)

    for (const [prop, value] of Object.entries(v)) {
      this.setPropertyValue(
        this.schema,
        this.initialValue,
        properties,
        prop,
        value,
      )
    }

    this.properties = properties
  }

  setTouched() {
    for (const state of Object.values(this.properties ?? {})) {
      if (state) {
        state.setTouched()
      }
    }
  }

  /**
   * Create the properties object and populate fields with initial values.
   */
  private createObject(
    schema: JSONSchemaOf<"object">,
    initialValue: Record<string, unknown> | null | undefined,
  ) {
    const properties: Record<string, FieldState<unknown>> = {}

    for (const [prop, propSchema] of Object.entries(schema.properties ?? {})) {
      const isRequired = !!schema.required && schema.required.includes(prop)
      const propValue = this.getPropertyInitialValue(schema, initialValue, prop)

      if (isRequired || propValue !== undefined) {
        properties[prop] = this.createPropertyState(prop, propSchema, propValue)
      }
    }

    this.properties = properties
    return this.properties
  }

  private setPropertyValue(
    objSchema: JSONSchemaOf<"object">,
    objInitialValue: Record<string, unknown> | null | undefined,
    properties: Record<string, FieldState<unknown> | undefined>,
    prop: string,
    value: unknown,
  ) {
    let state = properties[prop]

    if (!state) {
      const initialValue = this.getPropertyInitialValue(
        objSchema,
        objInitialValue,
        prop,
      )
      const schema = objSchema.properties ? objSchema.properties[prop] : {}
      state = this.createPropertyState(prop, schema, initialValue)
      properties[prop] = state
    }

    state.setValue(value)
  }

  private createPropertyState(
    prop: string,
    schema: JSONSchema,
    initialValue: unknown | null,
  ) {
    const getErrors = () => {
      const parentErr = this.getErrors()
      return parentErr ? parentErr[prop] : undefined
    }

    return _createState(schema, getErrors, initialValue ?? null)
  }

  private getPropertyInitialValue(
    objSchema: JSONSchemaOf<"object">,
    objInitialValue: Record<string, unknown> | null | undefined,
    prop: string,
  ) {
    const propSchema = objSchema.properties ? objSchema.properties[prop] : {}
    const propDefault =
      typeof propSchema == "object" ? propSchema.default : undefined
    const propInitial = objInitialValue ? objInitialValue[prop] : undefined
    return propInitial !== undefined ? propInitial : propDefault
  }

  reset() {
    this.setValue(this.initialValue !== undefined ? this.initialValue : {})
  }
}

const _createState = (
  schema: JSONSchema,
  getErrors: GetErrors,
  initialValue: unknown | null | undefined,
): FieldState<unknown> => {
  if (typeof schema == "boolean") {
    // not a supported case...
    return new ScalarFieldState({}, () => undefined)
  } else if (isType("object", schema)) {
    return new ObjectFieldStateImpl(
      schema,
      getErrors,
      initialValue as Record<string, unknown> | null,
    )
  } else {
    return new ScalarFieldState(schema, getErrors, initialValue)
  }
}

/**
 * Create a {@link FieldState} for a schema.
 * @param schema - the schema
 * @param initialValue - the initial value
 * @returns a pair of the field state and a function to get the validated value
 */
export const createState = (
  schema: JSONSchema,
  initialValue?: unknown | null,
): [FieldState<unknown>, () => unknown] => {
  const zodSchema = createSchema(schema)

  const stateBox = observable.box<FieldState<unknown> | null>(null)

  const validationResult = computed(() => {
    const state = stateBox.get()
    if (state == null) {
      return null
    }

    return zodSchema.safeParse(state.value)
  })

  const errors = computed(() => {
    const res = validationResult.get()
    if (!res || res.success) {
      return undefined
    } else {
      return res.error.format() as ErrorObj
    }
  })

  const validValue = computed(() => {
    const res = validationResult.get()

    if (res?.success) {
      return toJS(res.data)
    }
  })

  const state = _createState(schema, () => errors.get(), initialValue)
  stateBox.set(state)
  return [state, () => validValue.get()]
}
