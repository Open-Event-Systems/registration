import { FieldState, Schema, Validator } from "#src/types.js"
import { action, computed, makeObservable, observable } from "mobx"

export class FieldStateBase<T = unknown> implements FieldState<T> {
  protected _schema: Schema
  protected initialValue: unknown
  protected validator: Validator<T>
  public value: unknown
  public touched = false

  get schema(): Schema {
    return this._schema
  }

  get validValue(): T {
    throw new Error("Method not implemented.")
  }

  get error(): string | undefined {
    throw new Error("Method not implemented.")
  }

  constructor(schema: Schema, validator: Validator<T>, initialValue?: unknown) {
    this._schema = schema
    this.initialValue = initialValue
    this.validator = validator
    this.value = initialValue ?? schema.default

    makeObservable(this, {
      value: observable,
      touched: observable,
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
