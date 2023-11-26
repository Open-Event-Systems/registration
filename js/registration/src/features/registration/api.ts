import { Registration, RegistrationAPI } from "#src/features/registration"
import { Wretch } from "wretch"
import queryString from "wretch/addons/queryString"

export const createRegistrationAPI = (wretch: Wretch): RegistrationAPI => {
  wretch = wretch.url("/registrations")

  return {
    list(query, options = {}) {
      let req = wretch.addon(queryString)
      if (query) {
        req = req.query({ q: query })
      }

      for (const [opt, val] of Object.entries(options)) {
        if (val) {
          req = req.query({ [opt]: val })
        }
      }

      return {
        queryKey: ["registrations", { query: query, ...options }],
        initialPageParam: null,
        getNextPageParam(results) {
          return results ? results[results.length - 1]?.id : undefined
        },
        async queryFn({ pageParam }) {
          let pageReq = req
          if (pageParam) {
            pageReq = req.query({ after: pageParam })
          }

          const res = await pageReq.get().res()
          const data = res.json()
          return data
        },
      }
    },
    read(id) {
      const req = wretch.url(`/${id}`)

      return {
        queryKey: ["registrations", id],
        async queryFn() {
          return await req.get().json<Registration>()
        },
      }
    },
    update() {
      return {
        async mutationFn(registration) {
          let req = wretch.url(`/${registration.id}`)
          const ifMatch = `W/"${registration.version}"`
          req = req.headers({ "If-Match": ifMatch })

          const res = await req.json(registration).put().json<Registration>()
          return res
        },
      }
    },
    complete(id) {
      return {
        async mutationFn() {
          return await wretch.url(`/${id}/complete`).put().json<Registration>()
        },
      }
    },
    cancel(id) {
      return {
        async mutationFn() {
          return await wretch.url(`/${id}/cancel`).put().json<Registration>()
        },
      }
    },
  }
}
