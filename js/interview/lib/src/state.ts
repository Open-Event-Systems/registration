import { createZodSchema, isType } from "#src/schemax.js"
import { FieldState, Schema, ValidationResult, Validator } from "#src/types.js"
import { action, computed, makeObservable, observable } from "mobx"
import { z } from "zod"

export class FieldStateBase<T = unknown, S extends Schema = Schema>
  implements FieldState<T>
{
  protected _schema: S
  protected initialValue: unknown
  protected validator: Validator<T | null | undefined>
  public value: unknown
  public touched = false

  get schema(): S {
    return this._schema
  }

  private get validationResult(): ValidationResult<T | null | undefined> {
    return this.validator(this.value)
  }

  get validValue(): T | null | undefined {
    const res = this.validationResult
    if (res.success) {
      return res.value
    } else {
      return undefined
    }
  }

  get error(): string | undefined {
    const res = this.validationResult
    if (res.success) {
      return undefined
    } else {
      return res.error
    }
  }

  constructor(
    schema: S,
    validator: Validator<T | null | undefined>,
    initialValue?: unknown,
  ) {
    this._schema = schema
    this.initialValue = initialValue
    this.validator = validator
    this.value = initialValue ?? schema.default

    makeObservable<this, "validationResult">(this, {
      value: observable,
      touched: observable,
      validationResult: computed,
      validValue: computed,
      error: computed,
      reset: action,
    })
  }

  reset() {
    this.value = this.initialValue
    this.touched = false
  }
}

export class RootSchemaState {
  private zodSchema: z.ZodType<unknown>

  constructor(schema: Schema) {
    this.zodSchema = createZodSchema(schema)
  }
}

const createState = (
  schema: Schema,
  root: RootSchemaState,
  path?: (string | number)[],
): FieldState => {
  // create field state

  if (isType(schema, "object")) {
    for (const [prop, subschema] of Object.entries(schema.properties ?? {})) {
      const newPath = [...(path ?? []), prop]
      const substate = createState(subschema, root, newPath)
    }
  }
}
