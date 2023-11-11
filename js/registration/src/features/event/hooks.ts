import { placeholderWretch } from "#src/config/api"
import { EventStore } from "#src/features/event/stores"
import { createContext, useContext } from "react"

export const EventStoreContext = createContext(
  new EventStore(placeholderWretch),
)

export const useEvents = () => useContext(EventStoreContext)
