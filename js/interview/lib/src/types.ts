import {
  JSONSchema7,
  JSONSchema7Definition,
  JSONSchema7TypeName,
} from "json-schema"

/**
 * Form values type.
 */
export type FormValues = Record<string, unknown>

export type JSONSchema = JSONSchema7Definition
export type JSONSchemaOf<T extends JSONSchema7TypeName> = JSONSchema7 & {
  type: T | JSONSchema7TypeName[]
}

// extend schema
declare module "json-schema" {
  interface JSONSchema7 {
    "x-type"?: string
    "x-component"?: string
    "x-input-mode"?: string
    "x-autocomplete"?: string
    "x-minimum"?: string
    "x-maximum"?: string
    "x-primary"?: boolean
  }
}

export interface AskResult {
  type: "question"
  schema: JSONSchema
}

export interface ExitResult {
  type: "exit"
  title: string
  description?: string
}

/**
 * Not returned by the server, but substituted when handling errors.
 */
export interface ErrorResult {
  type: "error"
  description?: string
}

/**
 * Interview update result content.
 */
export type Result = AskResult | ExitResult | ErrorResult

export interface IncompleteStateResponse {
  state: string
  complete?: false
  content: Result | null
  update_url?: string
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
   * The record ID, derived from the state data.
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
 * The interview service API interface.
 */
export interface InterviewAPI {
  updateState(
    record: InterviewStateRecord,
    responses?: FormValues,
  ): Promise<InterviewStateRecord>
}

/**
 * Interview record storage.
 */
export interface InterviewRecordStore {
  /**
   * Get an {@link InterviewStateRecord}.
   * @param id - the record ID
   */
  getRecord(id: string): InterviewStateRecord | undefined

  /**
   * Save the state record.
   * @param record - the state record
   */
  saveRecord(record: InterviewStateRecord): void
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

/**
 * Holds the state for a form field.
 */
export interface FieldState<T> {
  /**
   * The {@link JSONSchema7} for this field.
   */
  get schema(): JSONSchema7

  /**
   * The current value of the field.
   */
  get value(): T | null

  /**
   * Set the current value.
   */
  setValue(v: T | null): void

  /**
   * The error message for the current value, or undefined if valid.
   */
  get error(): string | undefined

  /**
   * Whether the current value is valid.
   */
  get isValid(): boolean

  /**
   * Whether the field has been interacted with.
   */
  get touched(): boolean

  /**
   * Mark the field as having been interacted with.
   */
  setTouched(): void

  /**
   * Reset the field to its initial state.
   */
  reset(): void
}

/**
 * A {@link FieldState} for an object.
 */
export interface ObjectFieldState extends FieldState<Record<string, unknown>> {
  readonly properties: Record<string, FieldState<unknown> | undefined> | null
}
