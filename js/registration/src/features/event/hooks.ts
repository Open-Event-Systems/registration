import { placeholderWretch } from "#src/config/api"
import { createEventAPI } from "#src/features/event/api"
import { EventAPI } from "#src/features/event/types"
import { createContext, useContext } from "react"

export const EventAPIContext = createContext(createEventAPI(placeholderWretch))

export const useEventAPI = (): EventAPI => useContext(EventAPIContext)
