import { SelfServiceRegistrationListResponse } from "#src/features/selfservice/types.js"
import { Wretch } from "wretch"
import { queryStringAddon } from "wretch/addons"

/**
 * Fetch the list of self service registrations.
 * @param wretch - The wretch instance.
 * @param eventId - The event ID, or undefined to list for all events.
 * @returns
 */
export const listSelfServiceRegistrations = async (
  wretch: Wretch,
  eventId?: string,
  accessCode?: string
): Promise<SelfServiceRegistrationListResponse> => {
  let req = wretch.url("/self-service/registrations").addon(queryStringAddon)

  if (eventId) {
    req = req.query({ event_id: eventId })
  }

  if (accessCode) {
    req = req.query({ access_code: accessCode })
  }

  return await req.get().json<SelfServiceRegistrationListResponse>()
}
