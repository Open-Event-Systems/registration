import { InterviewOption } from "#src/features/cart/types"
import { Registration, RegistrationAPI } from "#src/features/registration"
import { StateResponse } from "@open-event-systems/interview-lib"
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
    listAddInterviews(eventId: string) {
      return {
        queryKey: ["registrations", "interviews", eventId],
        async queryFn() {
          return await wretch
            .url("/interviews")
            .addon(queryString)
            .query({ event_id: eventId })
            .get()
            .json<InterviewOption[]>()
        },
      }
    },
    readAddInterview(eventId, interviewId) {
      return {
        queryKey: ["registrations", "new-interview", { eventId, interviewId }],
        async queryFn() {
          return await wretch
            .url("/new-interview")
            .addon(queryString)
            .query({ event_id: eventId, interview_id: interviewId })
            .get()
            .json<StateResponse>()
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
    // TODO: this should be parametrized by ID
    update() {
      return {
        mutationKey: ["registrations"],
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
        mutationKey: ["registrations", id, "complete"],
        async mutationFn() {
          return await wretch.url(`/${id}/complete`).put().json<Registration>()
        },
      }
    },
    cancel(id) {
      return {
        mutationKey: ["registrations", id, "cancel"],
        async mutationFn() {
          return await wretch.url(`/${id}/cancel`).put().json<Registration>()
        },
      }
    },
    listChangeInterviews(id) {
      return {
        queryKey: ["registrations", id, "interviews"],
        async queryFn() {
          return await wretch
            .url(`/${id}/interviews`)
            .get()
            .json<InterviewOption[]>()
        },
      }
    },
    readChangeInterview(id, interviewId) {
      return {
        queryKey: ["registrations", id, "interviews", interviewId],
        async queryFn() {
          const req = wretch
            .url(`/${id}/new-interview`)
            .addon(queryString)
            .query({ interview_id: interviewId })

          return await req.get().json<StateResponse>()
        },
      }
    },
    readCheckinInterview(id) {
      return {
        queryKey: ["registrations", id, "check-in"],
        async queryFn() {
          return await wretch.url(`/${id}/check-in`).get().json<StateResponse>()
        },
      }
    },
    completeCheckinInterview(id) {
      return {
        mutationKey: ["registrations", id, "check-in"],
        async mutationFn(record) {
          const response = record.stateResponse
          if (!response.complete || !response.target_url) {
            return
          }

          await wretch
            .url(response.target_url, true)
            .json({ state: response.state })
            .post()
            .res()
        },
      }
    },
  }
}
