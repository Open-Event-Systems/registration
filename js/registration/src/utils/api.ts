/**
 * Not found error.
 */
export class NotFoundError extends Error {
  status = 404 as const

  constructor(message = "Not found") {
    super(message)
  }
}

/**
 * Return whether an object is a {@link Response}-like object with an error status.
 */
export const isResponseError = (e: unknown): e is { status: number } =>
  typeof e == "object" &&
  e != null &&
  "status" in e &&
  typeof e.status == "number" &&
  e.status >= 400

/**
 * Test if an error is a "not found" error.
 */
export const isNotFoundError = (
  e: unknown,
): e is NotFoundError | { status: 404 } =>
  e instanceof NotFoundError || isResponseError(e)

/**
 * Test if an error is an error from the backend with "detail" as a property.
 */
export const isAPIError = (e: unknown): e is { json: { detail: string } } =>
  isResponseError(e) &&
  "json" in e &&
  typeof e.json == "object" &&
  !!e.json &&
  "detail" in e.json &&
  typeof e.json.detail == "string"

/**
 * Wrap a promise to resolve with null in the case of a not found error.
 */
export const handleNotFound = <T>(promise: Promise<T>): Promise<T | null> => {
  return promise.catch((err) => {
    if (isNotFoundError(err)) {
      return null
    }
    return Promise.reject(err)
  })
}
