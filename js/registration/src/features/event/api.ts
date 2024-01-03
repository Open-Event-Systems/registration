import { Event, EventAPI } from "#src/features/event/types"
import { NotFoundError } from "#src/utils/api"
import { QueryClient } from "@tanstack/react-query"
import { Wretch } from "wretch"

export const createEventAPI = (
  wretch: Wretch,
  client: QueryClient,
): EventAPI => ({
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
  read(id) {
    return {
      queryKey: ["events", id],
      queryFn: async () => {
        const events = await client.fetchQuery<Map<string, Event>>(this.list())
        const result = events.get(id)
        if (!result) {
          throw new NotFoundError()
        }
        return result
      },
    }
  },
})
