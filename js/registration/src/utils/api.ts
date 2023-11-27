import { NextFunc } from "#src/types/api"
import { Wretch, WretchError } from "wretch"

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
