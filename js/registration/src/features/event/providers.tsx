import { EventStoreContext } from "#src/features/event/hooks"
import { EventStore } from "#src/features/event/stores"
import { useWretch } from "#src/hooks/api"
import { ReactNode, useState } from "react"

export const EventStoreProvider = ({ children }: { children?: ReactNode }) => {
  const wretch = useWretch()
  const [store] = useState(() => new EventStore(wretch))
  return (
    <EventStoreContext.Provider value={store}>
      {children}
    </EventStoreContext.Provider>
  )
}
