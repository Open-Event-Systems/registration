import { observer, useLocalObservable } from "mobx-react-lite"
import {
  SearchContext,
  Search as SearchStore,
} from "#src/features/registration/stores/search"
import { Search } from "#src/features/registration/components/search/Search"
import { EventAPIContext, useEvents } from "#src/features/event/hooks"
import {
  RegistrationAPIContext,
  useRegistrationStore,
} from "#src/features/registration/hooks"
import {
  useQuery,
  useQueryClient,
  useSuspenseQuery,
} from "@tanstack/react-query"
import { eventsQuery } from "#src/features/event/api"
import { useContext } from "react"

export const SearchPage = observer(() => {
  const client = useQueryClient()
  const eventAPI = useContext(EventAPIContext)
  const registrationAPI = useContext(RegistrationAPIContext)
  const events = useSuspenseQuery(eventsQuery(eventAPI))

  const [firstEvent] = events.data.values()
  const state = useLocalObservable(
    () => new SearchStore(client, registrationAPI, firstEvent?.id),
  )

  return (
    <SearchContext.Provider value={state}>
      <Search
        events={Array.from(events.data.values(), (e) => ({
          id: e.id,
          name: e.name,
        }))}
        getLink={(r) => {
          let url = window.location.href
          if (!url.endsWith("/")) {
            url = url + "/"
          }

          url += r.id

          return [url, r.id]
        }}
      />
    </SearchContext.Provider>
  )
})
