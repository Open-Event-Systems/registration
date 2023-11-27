import { NextFunc } from "#src/types/api"
import { Wretch } from "wretch"

/**
 * Not found error.
 */
export class NotFoundError extends Error {
  status: 404 = 404

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

/**
 * Get a {@link NextFunc} for a paginated response.
 */
export function getNextFunc<T>(
  wretch: Wretch,
  handler: (response: Response) => Promise<T>,
  link: string,
): NextFunc<T> | null
export function getNextFunc<T>(
  wretch: Wretch,
  handler: (response: Response) => Promise<T>,
  response: Response,
): NextFunc<T> | null
export function getNextFunc<T>(
  wretch: Wretch,
  handler: (response: Response) => Promise<T>,
  linkOrResponse: Response | string,
): NextFunc<T> | null {
  let url
  if (typeof linkOrResponse == "string") {
    url = linkOrResponse
  } else {
    url = getNextLink(linkOrResponse)
  }

  const nextUrl = url

  if (!nextUrl) {
    return null
  }

  return async () => {
    const response = await wretch.url(nextUrl, true).get().res()
    const result = await handler(response)
    const nextFunc = getNextFunc(wretch, handler, response)
    return [result, nextFunc]
  }
}

/**
 * Get the "next" link from a response.
 */
export const getNextLink = (response: Response): string | undefined => {
  const linkHeader = response.headers.get("Link")
  if (!linkHeader) {
    return undefined
  }

  const nextMatch = /<(.*?)>;\s*rel="next"/.exec(linkHeader) ?? []
  return nextMatch[1]
}
