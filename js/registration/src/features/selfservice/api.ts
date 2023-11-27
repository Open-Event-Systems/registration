import { placeholderWretch } from "#src/config/api"
import {
  SelfServiceAPI,
  SelfServiceEvent,
  SelfServiceRegistrationListResponse,
} from "#src/features/selfservice/types"
import { createContext } from "react"
import { Wretch, WretchResponse } from "wretch"
import queryString from "wretch/addons/queryString"

/**
 * Fetch the list of self service registrations.
 * @param wretch - The wretch instance.
 * @param eventId - The event ID, or undefined to list for all events.
 * @returns
 */
export const listSelfServiceRegistrations = async (
  wretch: Wretch,
  eventId?: string,
  accessCode?: string,
): Promise<SelfServiceRegistrationListResponse> => {
  let req = wretch.url("/self-service/registrations").addon(queryString)

  if (eventId) {
    req = req.query({ event_id: eventId })
  }

  if (accessCode) {
    req = req.query({ access_code: accessCode })
  }

  return await req.get().json<SelfServiceRegistrationListResponse>()
}

/**
 * Check if an access code is valid.
 * @param wretch - The wretch instance.
 * @param eventId - The event ID.
 * @param accessCode - The access code.
 */
export const checkAccessCode = async (
  wretch: Wretch,
  eventId: string,
  accessCode: string,
): Promise<true> => {
  await wretch
    .url(`/access-code/${accessCode}`)
    .addon(queryString)
    .query({ event_id: eventId })
    .get()
    .res<WretchResponse>()

  return true
}

export const createSelfServiceAPI = (wretch: Wretch): SelfServiceAPI => {
  wretch = wretch.url("/self-service")

  return {
    listEvents() {
      return {
        queryKey: ["self-service", "events"],
        async queryFn() {
          const res = await wretch
            .url("/events")
            .get()
            .json<SelfServiceEvent[]>()
          return new Map(res.map((e) => [e.id, e]))
        },
        initialData: new Map(),
        staleTime: Infinity,
        initialDataUpdatedAt: 0,
      }
    },
    listRegistrations(options = {}) {
      return {
        queryKey: ["self-service", "registrations", options],
        async queryFn() {
          let req = wretch.url("/registrations").addon(queryString)

          if (options.eventId) {
            req = req.query({ event_id: options.eventId })
          }

          if (options.accessCode) {
            req = req.query({ access_code: options.accessCode })
          }

          return await req.get().json<SelfServiceRegistrationListResponse>()
        },
        initialData: { add_options: [], registrations: [] },
        staleTime: Infinity,
        initialDataUpdatedAt: 0,
      }
    },
  }
}

export const SelfServiceAPIContext = createContext(
  createSelfServiceAPI(placeholderWretch),
)
