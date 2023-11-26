import { Event, EventAPI } from "#src/features/event/types"
import { QueryOptions } from "@tanstack/react-query"
import { Wretch } from "wretch"

/**
 * Fetch a list of events.
 */
export const listEvents = async (
  wretch: Wretch,
): Promise<Map<string, Event>> => {
  const res = await wretch.url("/events").get().json<Event[]>()
  const map = new Map<string, Event>()

  for (const event of res) {
    map.set(event.id, event)
  }

  return map
}

export const createEventAPI = (wretch: Wretch): EventAPI => ({
  async list() {
    return wretch.url("/events").get().json<Event[]>()
  },
})

export const eventsQuery = (api: EventAPI) =>
  ({
    queryKey: ["events"],
    queryFn: async () => {
      const events = await api.list()
      return new Map(events.map((e) => [e.id, e]))
    },
  }) satisfies QueryOptions
