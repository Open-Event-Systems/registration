import { JSONSchema7 } from "json-schema"

/**
 * Form values type.
 */
export type FormValues = Record<string, unknown>

export type JSONSchema = JSONSchema7

// extend schema
declare module "json-schema" {
  interface JSONSchema7 {
    "x-type"?: string
    "x-component"?: string
    "x-input-mode"?: string
    "x-autocomplete"?: string
    "x-minimum"?: string
    "x-maximum"?: string
  }
}

export interface AskResult {
  type: "question"
  schema: JSONSchema
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

export type ValidationResult<T> =
  | {
      success: true
      value: T
    }
  | {
      success: false
      error: string
    }

export type Validator<T> = (value: unknown) => ValidationResult<T>

/**
 * Field state interface.
 */
export interface FieldState<T = unknown> {
  /**
   * The schema.
   */
  get schema(): JSONSchema

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
