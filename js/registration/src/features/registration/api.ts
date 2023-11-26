import {
  RegistrationAPI,
  RegistrationSearchResult,
} from "#src/features/registration"
import { getNextFunc } from "#src/util/api"
import { QueryOptions } from "@tanstack/react-query"
import { Wretch } from "wretch"
import queryString from "wretch/addons/queryString"

export const createRegistrationAPI = (wretch: Wretch): RegistrationAPI => {
  wretch = wretch.url("/registrations")

  return {
    async list(query, options = {}) {
      let req = wretch.addon(queryString)

      if (query) {
        req = req.query({ q: query })
      }

      for (const [opt, val] of Object.entries(options)) {
        if (val) {
          req = req.query({ [opt]: val })
        }
      }

      const handler = async (
        response: Response,
      ): Promise<RegistrationSearchResult[]> => {
        return await response.json()
      }

      const response = await req.get().res()
      const result = await handler(response)
      const next = getNextFunc(wretch, handler, response)
      return [result, next]
    },
  }
}

export const searchQuery = (
  api: RegistrationAPI,
  query?: string,
  options: { all?: boolean; event_id?: string } = {},
) =>
  ({
    queryKey: [query, options],
    async queryFn() {
      return await api.list(query, options)
    },
  }) satisfies QueryOptions
