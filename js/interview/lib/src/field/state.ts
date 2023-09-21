import { createValidator } from "#src/field/validation.js"
import {
  Schema,
  ValidationError,
  ValidationResult,
  Validator,
} from "#src/types.js"
import { computed, makeObservable, observable } from "mobx"

export interface FieldState {
  /**
   * The schema for the field.
   */
  get schema(): Schema

  /**
   * The current value.
   */
  get value(): unknown
  set value(value: unknown)

  /**
   * The value used for validation.
   */
  get validValue(): unknown

  /**
   * Whether the field has been interacted with.
   */
  get touched(): boolean
  set touched(touched: boolean)

  /**
   * The validation errors for the current value.
   */
  get errors(): ValidationError[]

  /**
   * Whether the field is valid.
   */
  get isValid(): boolean
}

abstract class BaseFieldState {
  schema: Schema
  protected validator: Validator

  constructor(schema: Schema) {
    this.schema = schema
    this.validator = createValidator(schema)
  }
}

export class ScalarFieldState extends BaseFieldState implements FieldState {
  value: unknown = null
  touched = false

  get validationResult(): ValidationResult {
    return this.validator(this.value)
  }

  get validValue(): unknown {
    return this.validationResult.value
  }

  get errors(): ValidationError[] {
    return this.validationResult.errors
  }

  get isValid(): boolean {
    return this.errors.length == 0
  }

  constructor(schema: Schema) {
    super(schema)

    if (schema.default) {
      this.value = schema.default
    }

    makeObservable(this, {
      value: observable,
      touched: observable,
      validationResult: computed,
      validValue: computed,
      errors: computed,
      isValid: computed,
    })
  }
}

export class ObjectFieldState extends BaseFieldState implements FieldState {
  properties: Record<string, FieldState> | null = null

  get value(): Record<string, unknown> | null {
    if (this.properties == null) {
      return null
    } else {
      const value: Record<string, unknown> = {}

      for (const [key, propState] of Object.entries(this.properties)) {
        value[key] = propState.value
      }

      return value
    }
  }

  set value(value: Record<string, unknown> | null) {
    if (value == null) {
      this.properties = null
    } else {
      this.properties = {}

      for (const [key, schema] of Object.entries(
        this.schema.properties ?? {},
      )) {
        this.properties[key] = createState(schema)

        if (key in value) {
          this.properties[key].value = value[key]
        }
      }
    }
  }

  get touched(): boolean {
    return (
      this.properties == null ||
      Object.values(this.properties).every((p) => p.touched)
    )
  }

  set touched(touched: boolean) {
    if (this.properties != null) {
      Object.values(this.properties).forEach((p) => (p.touched = touched))
    }
  }

  get validationResult(): ValidationResult {
    return this.validator(this.value)
  }

  get validValue(): Record<string, unknown> | null {
    return this.validationResult.value as Record<string, unknown> | null
  }

  get isValid(): boolean {
    return this.isPropertiesValid && this.errors.length == 0
  }

  get errors(): ValidationError[] {
    return this.validationResult.errors
  }

  get isPropertiesValid(): boolean {
    return Object.values(this.properties ?? {}).every((p) => p.isValid)
  }

  constructor(schema: Schema) {
    super(schema)
    makeObservable(this, {
      properties: observable,
      value: computed,
      validationResult: computed,
      validValue: computed,
      touched: computed,
      isValid: computed,
      errors: computed,
      isPropertiesValid: computed,
    })
  }
}

/**
 * Create a {@link FieldState} for a schema.
 * @param schema
 * @returns
 */
export const createState = (schema: Schema): FieldState => {
  if (schema.type == "object") {
    return new ObjectFieldState(schema)
  } else if (schema["x-type"] == "select" || schema["x-type"] == "button") {
    return new ScalarFieldState(schema)
  } else if (schema.type == "array") {
    throw new Error(`Unsupported schema type: ${schema.type}`)
  } else {
    return new ScalarFieldState(schema)
  }
}
