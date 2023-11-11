import { placeholderWretch } from "#src/config/api"
import {
  Registration,
  RegistrationAPI,
  RegistrationSearchResult,
} from "#src/features/registration/types"
import { createContext, useContext } from "react"
import { Wretch } from "wretch"
import queryString from "wretch/addons/queryString"

export const createRegistrationAPI = (baseWretch: Wretch): RegistrationAPI => {
  const wretch = baseWretch.url("/registrations")
  return {
    async search(query, options) {
      let req = wretch.addon(queryString)

      if (options?.page) {
        req = req.query({ page: options.page })
      }

      if (options?.per_page) {
        req = req.query({ per_page: options.per_page })
      }

      if (query) {
        req = req.query({ q: query })
      }

      return await req.get().json<RegistrationSearchResult[]>()
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
          return undefined
        })
        .json<Registration | undefined>()
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
