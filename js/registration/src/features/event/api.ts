import { Event, EventAPI } from "#src/features/event/types"
import { Wretch } from "wretch"

export const createEventAPI = (wretch: Wretch): EventAPI => ({
  list: () => ({
    queryKey: ["events"],
    initialData: new Map(),
    initialDataUpdatedAt: 0,
    staleTime: Infinity,
    async queryFn() {
      const events = await wretch.url("/events").get().json<Event[]>()
      return new Map(events.map((e) => [e.id, e]))
    },
  }),
})
