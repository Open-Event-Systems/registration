import { placeholderWretch } from "#src/config/api"
import { createEventAPI } from "#src/features/event/api"
import { EventStore } from "#src/features/event/stores"
import { EventAPI } from "#src/features/event/types"
import { createContext, useContext } from "react"

export const EventAPIContext = createContext(createEventAPI(placeholderWretch))

export const EventStoreContext = createContext(
  new EventStore(placeholderWretch),
)

export const useEvents = () => useContext(EventStoreContext)

export const useEventAPI = (): EventAPI => useContext(EventAPIContext)
