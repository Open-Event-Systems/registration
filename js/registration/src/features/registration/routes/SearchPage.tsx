import { observer, useLocalObservable } from "mobx-react-lite"
import {
  SearchContext,
  Search as SearchStore,
} from "#src/features/registration/stores/search"
import { Search } from "#src/features/registration/components/search/Search"
import { EventAPIContext } from "#src/features/event/hooks"
import { RegistrationAPIContext } from "#src/features/registration/hooks"
import { useInfiniteQuery, useQuery } from "@tanstack/react-query"
import { useContext } from "react"

export const SearchPage = observer(() => {
  const eventAPI = useContext(EventAPIContext)
  const registrationAPI = useContext(RegistrationAPIContext)
  const events = useQuery(eventAPI.list())

  const [firstEvent] = events.data.values()
  const state = useLocalObservable(
    () => new SearchStore(registrationAPI, firstEvent?.id),
  )

  const { data, hasNextPage, fetchNextPage } = useInfiniteQuery(
    state.queryOptions,
  )

  return (
    <SearchContext.Provider value={state}>
      <Search
        events={Array.from(events.data.values(), (e) => ({
          id: e.id,
          name: e.name,
        }))}
        registrations={data ? flatten(data.pages) : undefined}
        hasMore={hasNextPage}
        onMore={async () => {
          await fetchNextPage()
        }}
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

const flatten = <T,>(data: T[][]): T[] => {
  const flattened = []
  for (const page of data) {
    flattened.push(...page)
  }
  return flattened
}
