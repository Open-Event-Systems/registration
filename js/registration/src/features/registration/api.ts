import { placeholderWretch } from "#src/config/api"
import { RegistrationSearchResult } from "#src/features/registration"
import {
  NextFunc,
  Registration,
  RegistrationAPI,
} from "#src/features/registration/types"
import { createContext, useContext } from "react"
import { Wretch } from "wretch"
import queryString from "wretch/addons/queryString"

export const createRegistrationAPI = (baseWretch: Wretch): RegistrationAPI => {
  const wretch = baseWretch.url("/registrations")
  return {
    async search(query, options = {}) {
      let req = wretch.addon(queryString)

      if (query) {
        req = req.query({ q: query })
      }

      for (const [opt, val] of Object.entries(options)) {
        if (val) {
          req = req.query({ [opt]: val })
        }
      }

      return await getSearchResults(req as Wretch)
    },
    async create(registration) {
      return await wretch.json(registration).post().json<Registration>()
    },
    async fromResponse(response) {
      return await response.json()
    },
    async read(id) {
      return await wretch
        .url(`/${id}`)
        .get()
        .notFound(() => {
          return null
        })
        .json<Registration | null>()
    },
    async update(registration) {
      const headers = {
        "If-Match": `W/"${registration.version}"`,
      }
      return await wretch
        .url(`/${registration.id}`)
        .json(registration)
        .headers(headers)
        .put()
        .json<Registration>()
    },
    async delete(id) {
      await wretch.url(`/${id}`).delete().text()
    },
  }
}

export const RegistrationAPIContext = createContext(
  createRegistrationAPI(placeholderWretch),
)

export const useRegistrationAPI = () => useContext(RegistrationAPIContext)

const getSearchResults = async (
  wretch: Wretch,
): Promise<[RegistrationSearchResult[], NextFunc | null]> => {
  const res = await wretch.get().res()
  const body = await res.json()

  const linkHeader = res.headers.get("Link")
  const nextMatch = linkHeader
    ? /<(.*?)>; rel="next"/.exec(linkHeader) ?? []
    : []
  const nextUrl = nextMatch[1]

  let next = null
  if (nextUrl) {
    next = () => getSearchResults(wretch.url(nextUrl, true))
  }

  return [body, next]
}
