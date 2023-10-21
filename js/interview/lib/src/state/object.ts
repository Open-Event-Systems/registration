import {
  FieldState,
  ObjectSchema,
  Schema,
  ValidationResult,
  Validator,
} from "#src/types.js"

export class ObjectState implements FieldState<Record<string, unknown>> {
  private _schema: ObjectSchema
  private validator: Validator<Record<string, unknown> | null | undefined>
  private _substates: Record<string, FieldState> | null | undefined = {}
  touched = false

  get schema(): ObjectSchema {
    return this._schema
  }

  get value(): Record<string, unknown> | null | undefined {
    const obj: Record<string, unknown> = {}

    if (this._substates == null) {
      return this._substates
    }

    for (const [prop, state] of Object.entries(this._substates)) {
      obj[prop] = state.value
    }

    return obj
  }

  set value(v: Record<string, unknown> | null | undefined) {
    if (v == null) {
      this._substates = v
    } else {
      if (this._substates == null) {
        this._substates = {} // todo
      }

      for (const [prop, state] of Object.entries(this._substates)) {
        state.value = v[prop]
      }
    }
  }

  private get validationResult(): ValidationResult<
    Record<string, unknown> | null | undefined
  > {
    return this.validator(this.value)
  }

  get validValue(): Record<string, unknown> | null | undefined {
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
    schema: ObjectSchema,
    validator: Validator<Record<string, unknown> | null | undefined>,
    initialValue?: Record<string, unknown>,
  ) {
    this._schema = schema
    this.value = initialValue // todo create state
    this.validator = validator
  }

  reset(): void {
    throw new Error("Method not implemented.")
  }
}
