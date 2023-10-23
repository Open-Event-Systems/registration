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
 * A saved interview state.
 */
export interface InterviewStateRecord {
  /**
   * The record ID.
   */
  get id(): string

  /**
   * The {@link StateResponse}
   */
  get stateResponse(): StateResponse

  /**
   * The responses.
   */
  get fieldValues(): FormValues
  set fieldValues(values: FormValues)

  /**
   * The associated metadata.
   */
  get metadata(): InterviewStateMetadata
  set metadata(values: InterviewStateMetadata)
}

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

export interface ErrorObj {
  [key: string]: ErrorObj | string[] | undefined
  _errors?: string[]
}

export type FormPath = (string | number)[]

/**
 * Stores state for a form schema.
 */
export interface FormState {
  /**
   * The {@link JSONSchema} describing the form.
   */
  get schema(): JSONSchema | boolean

  /**
   * Get a value in the state.
   */
  getValue(path?: FormPath): unknown

  /**
   * Set a value in the state.
   */
  setValue(path: FormPath, value: unknown): void

  /**
   * Get an error object in the state.
   */
  getError(path?: FormPath): ErrorObj | undefined

  /**
   * Reset the state to its initial value.
   */
  reset(): void
}
