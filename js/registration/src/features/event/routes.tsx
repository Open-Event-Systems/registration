import { eventsQuery } from "#src/features/event/api"
import { EventStoreProvider } from "#src/features/event/providers"
import { EventAPI } from "#src/features/event/types"
import { QueryClient } from "@tanstack/react-query"
import { Outlet, RouteObject } from "react-router-dom"

export const EventStoreRoute = () => {
  return (
    <EventStoreProvider>
      <Outlet />
    </EventStoreProvider>
  )
}

export const eventsRoute = (
  client: QueryClient,
  apiPromise: Promise<EventAPI>,
) =>
  ({
    async loader() {
      const api = await apiPromise
      const query = eventsQuery(api)
      return client.ensureQueryData(query)
    },
  }) satisfies RouteObject
