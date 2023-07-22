import { WretchError } from "wretch"

/**
 * Check if an error is a {@link WretchError}.
 */
export const isWretchError = (e: unknown): e is WretchError => {
  return (
    e != null &&
    typeof e == "object" &&
    "name" in e &&
    "message" in e &&
    "status" in e &&
    "response" in e &&
    "url" in e
  )
}

export interface NotFoundError {
  status: 404
}

/**
 * Test if an exception is from a not found response.
 */
export const isNotFoundError = (e: unknown): e is NotFoundError => {
  return (
    (isWretchError(e) && e.status == 404) ||
    (e instanceof Error && "status" in e && e.status == 404)
  )
}

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
