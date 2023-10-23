import { createSchema, isType } from "#src/schema/json-schema.js"
import { ErrorObj, FormPath, FormState, JSONSchema } from "#src/types.js"
import { z } from "zod"

class FormStateImpl implements FormState {
  private zodSchema: z.ZodType<unknown>
  private _value: unknown
  private _error: ErrorObj | null = null

  get schema(): JSONSchema | boolean {
    return this._schema
  }

  constructor(
    private _schema: JSONSchema | boolean,
    private initialValue?: unknown,
  ) {
    this.zodSchema = createSchema(_schema)
    this._value = getDefault(_schema, initialValue)
  }

  public getValue(path?: FormPath): unknown {
    return walk(path ?? [], this._value)
  }

  public setValue(path: FormPath, newValue: unknown) {
    const curPath = [...path]

    if (curPath.length > 0) {
      const key = curPath[curPath.length - 1]
      curPath.splice(curPath.length - 1, 1)
      const obj = walk(curPath, this._value) as Record<string | number, unknown>
      obj[key] = newValue
    } else {
      this._value = newValue
    }

    const res = this.zodSchema.safeParse(this._value)
    if (res.success) {
      this._error = null
    } else {
      this._error = res.error.format()
    }
  }

  public getError(path?: FormPath): ErrorObj | undefined {
    return walk(path ?? [], this._error) as ErrorObj | undefined
  }

  reset() {
    this._value = getDefault(this._schema, this.initialValue)
  }
}

const walk = (path: FormPath, obj: unknown): unknown => {
  const curPath = [...path]
  let cur = obj
  while (curPath.length > 0 && cur != null) {
    cur = (cur as Record<string | number, unknown>)[curPath[0]]
    curPath.splice(0, 1)
  }
  return cur
}

const getDefault = (
  schema: JSONSchema | boolean,
  initialValue?: unknown,
): unknown => {
  if (typeof schema == "boolean") {
    return undefined
  }

  const defaultValue =
    initialValue !== undefined ? initialValue : schema.default

  if (isType("object", schema)) {
    if (defaultValue === null) {
      return defaultValue
    }

    const defaultProps: Record<string, unknown> = {}

    for (const [prop, subschema] of Object.entries(schema.properties ?? {})) {
      const propDefault =
        defaultValue != null
          ? (defaultValue as Record<string, unknown>)[prop]
          : undefined
      const propValue = getDefault(subschema, propDefault)

      if (propValue !== undefined) {
        defaultProps[prop] = propValue
      }
    }

    return defaultProps
  }

  return defaultValue
}

/**
 * Create a {@link FormState} for a schema.
 * @param schema - the schema
 * @param initialValue - the initial value
 * @returns the state
 */
export const createFormState = (
  schema: JSONSchema | boolean,
  initialValue?: unknown,
): FormState => {
  const obj = new FormStateImpl(schema, initialValue)
  return obj
}
