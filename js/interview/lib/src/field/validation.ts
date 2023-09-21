import {
  Schema,
  ValidationError,
  ValidationResult,
  Validator,
} from "#src/types.js"
import * as EmailValidator from "email-validator"
import * as psl from "psl"
import AjvModule, { ErrorObject } from "ajv"

import ajvFormats_ from "ajv-formats"
import ajvErrors_ from "ajv-errors"

import dayjs from "dayjs"

// FIXME: https://github.com/ajv-validator/ajv/issues/2047
const Ajv = AjvModule.default
const ajvErrors = ajvErrors_.default
const ajvFormats = ajvFormats_.default

const ajv = new Ajv({ allErrors: true, coerceTypes: false })

ajvErrors(ajv)
ajvFormats(ajv)

ajv.addVocabulary([
  "x-type",
  "x-autocomplete",
  "x-input-mode",
  "x-minimum",
  "x-maximum",
  "x-component",
  "x-primary",
])

const errorMessages = {
  type: "is invalid",
  required: "is required",
  nullable: "is required",
  pattern: "is invalid",
  format: "is invalid",
  const: "is invalid",
}

/**
 * Create a validator for a question schema.
 * @param schema - The schema.
 * @returns A {@link Validator} function.
 */
export const createValidator = (schema: Schema): Validator => {
  const validators: Validator[] = []

  if (schema["x-type"] == "text") {
    validators.push(createTextValidator(schema))
    validators.push(createSchemaValidator(schema))
  } else if (schema["x-type"] == "date") {
    validators.push(createSchemaValidator(schema))
    validators.push(createDateValidator(schema))
  } else {
    validators.push(createSchemaValidator(schema))
  }

  return (value: unknown) => runValidators(value, validators)
}

const runValidators = (
  value: unknown,
  validators: Validator[],
): ValidationResult => {
  return validators.reduce<ValidationResult>(
    (prevVal, validator) => {
      const result = validator(prevVal.value)
      return {
        value: result.value,
        errors: [...prevVal.errors, ...result.errors],
      }
    },
    { value: value, errors: [] },
  )
}

const createSchemaValidator = (schema: Schema): Validator => {
  const schemaValidator = ajv.compile({
    errorMessage: {
      ...errorMessages,
      ...getErrorMap(schema),
    },
    ...schema,
  })

  const validator = (value: unknown): ValidationResult => {
    if (schemaValidator(value)) {
      return { value, errors: [] }
    } else {
      return {
        value,
        errors: schemaValidator.errors
          ? schemaValidator.errors
              .reverse()
              .map((err) => getError(schema.title, err))
          : [],
      }
    }
  }

  return validator
}

const getErrorMap = (schema: Schema) => {
  const errors: Record<string, string> = {}

  if (schema.minimum) {
    errors.minimum = `must be at least ${schema.minimum}`
  }

  if (schema.maximum) {
    errors.maximum = `must be ${schema.maximum} or less`
  }

  if (schema.minItems) {
    errors.minItems = `must include at least ${schema.minItems} items`
  }

  if (schema.maxItems) {
    errors.maxItems = `must include ${schema.maxItems} or fewer items`
  }

  if (schema.minLength) {
    errors.minLength = `must have at least ${schema.minLength} characters`
  }

  if (schema.maxLength) {
    errors.maxLength = `must have ${schema.maxLength} characters or fewer`
  }

  if (schema.oneOf) {
    errors.oneOf = "is invalid"
  }

  if (schema.const) {
    errors.const = "is invalid"
  }

  if (schema["x-type"] == "text") {
    errors.type = "is required"
  }

  return errors
}

const createTextValidator = (schema: Schema): Validator => {
  return (value: unknown): ValidationResult => {
    if (typeof value == "string") {
      // text fields trim the string before performing other validation
      // also coerce the empty string to null
      const trimmed = value.trim() || null
      const errors = []

      // email format
      // this needs to be reworked...
      if (schema.format == "email") {
        const formatRes = validateEmail(trimmed)
        if (formatRes) {
          errors.push(formatRes)
        }
      }

      return { value: trimmed, errors: errors }
    } else {
      return { value: value, errors: [] }
    }
  }
}

const validateEmail = (value: string | null): ValidationError | null => {
  if (value != null) {
    if (!EmailValidator.validate(value)) {
      return { message: "Email is invalid", path: "/" }
    }

    const parts = value.split("@")
    const domain = parts[parts.length - 1]
    if (!psl.isValid(domain)) {
      return { message: "Email is invalid", path: "/" }
    }
  }

  return null
}

const createDateValidator = (schema: Schema): Validator => {
  const min = schema["x-minimum"] ? dayjs(schema["x-minimum"]) : undefined
  const max = schema["x-maximum"] ? dayjs(schema["x-maximum"]) : undefined

  return (value) => {
    if (typeof value == "string") {
      const parsed = dayjs(value)
      if (!parsed.isValid()) {
        return { value, errors: [{ message: "Invalid date", path: "/" }] }
      }

      if (min && parsed.isBefore(min)) {
        return {
          value,
          errors: [{ message: "Choose a later date", path: "/" }],
        }
      }

      if (max && parsed.isAfter(max)) {
        return {
          value,
          errors: [{ message: "Choose an earlier date", path: "/" }],
        }
      }
    }

    return {
      value,
      errors: [],
    }
  }
}

const getError = (
  name: string | null | undefined,
  errObj: ErrorObject,
): ValidationError => {
  return {
    path: errObj.instancePath,
    message: (name || "Field") + " " + (errObj.message ?? "is invalid"),
  }
}
