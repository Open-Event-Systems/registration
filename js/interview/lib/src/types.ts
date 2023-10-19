/**
 * Form values type.
 */
export type FormValues = Record<string, unknown>

export interface AskResult {
  type: "question"
  schema: Record<string, unknown>
}

export interface ExitResult {
  type: "exit"
  title: string
  description?: string | null
}

/**
 * Interview update result content.
 */
export type Result = AskResult | ExitResult

export interface IncompleteStateResponse {
  state: string
  complete?: false
  content: Result | null
  update_url: string
}

export interface CompleteStateResponse {
  state: string
  complete: true
  target_url?: string
}

/**
 * The response from an update request.
 */
export type StateResponse = IncompleteStateResponse | CompleteStateResponse

/**
 * Request body for updating an interview state.
 */
export interface StateRequest {
  state: string
  responses?: Record<string, unknown>
}

/**
 * Custom metadata associated with an interview state.
 */
export interface InterviewStateMetadata {
  [key: string]: unknown
}

/** Schema types. */

/**
 * Base schema properties.
 */
export interface SchemaBase {
  type?: SchemaTypeKeys | SchemaTypeKeys[]
  "x-type"?: string
  title?: string
  description?: string
  const?: unknown
  oneOf?: Schema[]
  "x-input-mode": string
  "x-autocomplete": string
}

export interface StringSchema extends SchemaBase {
  type: "string" | SchemaTypeKeys[]
  default?: string
  minLength?: number
  maxLength?: number
  pattern?: string
  format?: string
  "x-minimum"?: string
  "x-maximum"?: string
}

export interface NumberSchema extends SchemaBase {
  type: "number" | SchemaTypeKeys[]
  default?: number
  minimum?: number
  maximum?: number
}

export interface IntegerSchema extends SchemaBase {
  type: "integer" | SchemaTypeKeys[]
  default?: number
  minimum?: number
  maximum?: number
}

export interface ObjectSchema extends SchemaBase {
  type: "object" | SchemaTypeKeys[]
  default?: Record<string, unknown>
  properties?: {
    [name: string]: Schema
  }
  required?: string[]
}

export interface ArraySchema extends SchemaBase {
  type: "array" | SchemaTypeKeys[]
  default?: unknown[]
  minItems?: number
  maxItems?: number
  uniqueItems?: boolean
  items?: Schema
}

export interface BooleanSchema extends SchemaBase {
  type: "boolean" | SchemaTypeKeys[]
  default?: boolean
}

export interface NullSchema extends SchemaBase {
  type: "null" | SchemaTypeKeys[]
}

export interface SchemaTypeMap {
  string: StringSchema
  number: NumberSchema
  integer: IntegerSchema
  object: ObjectSchema
  array: ArraySchema
  boolean: BooleanSchema
  null: NullSchema
}

export type SchemaTypeKeys = keyof SchemaTypeMap

export type Schema = SchemaBase | SchemaTypeMap[SchemaTypeKeys]

/**
 * Field state interface.
 */
export interface FieldState<T = unknown> {
  /**
   * The schema.
   */
  get schema(): unknown // TODO

  /**
   * The stored value type.
   */
  get value(): unknown
  set value(v: unknown)

  /**
   * The validated/cast value type.
   */
  get validValue(): T | null | undefined

  /**
   * The error message, or undefined if valid.
   */
  get error(): string | undefined

  /**
   * Whether the field has been interacted with.
   */
  get touched(): boolean
  set touched(v: boolean)

  /**
   * Reset to the initial state.
   */
  reset(): void
}
