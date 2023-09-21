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
  complete: false
  content: Result | null
  update_url: string
}

export interface CompleteStateResponse {
  state: string
  complete: true
  target_url?: string | null
}

/**
 * The response from an update request.
 */
export type StateResponse = IncompleteStateResponse | CompleteStateResponse

/**
 * Interface of field types.
 *
 * Maps field type strings to JSON data types.
 */
export interface FieldTypes {
  text: string
  number: number
  date: string
  select: string | string[]
  button: string
}

/**
 * Additional schema properties.
 */
export interface ExtraSchemaProperties {
  title?: string
  description?: string
  "x-type"?: keyof FieldTypes
  "x-primary"?: boolean
  "x-minimum"?: string
  "x-maximum"?: string
  "x-component"?: string
}

/**
 * Loosely typed version of a JSON schema.
 */
export interface Schema extends ExtraSchemaProperties {
  type?:
    | "object"
    | "array"
    | "string"
    | "number"
    | "integer"
    | "boolean"
    | "null"
  properties?: Record<string, Schema>
  required?: string[]
  nullable?: boolean
  const?: unknown
  items?: Schema
  oneOf?: Schema[]
  [key: string]: unknown
}

export type ValidationError = {
  path: string
  message: string
}

export type ValidationResult = {
  value: unknown
  errors: ValidationError[]
}

export type Validator = (responses: unknown) => ValidationResult

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
