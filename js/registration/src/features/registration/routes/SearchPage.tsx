import { observer, useLocalObservable } from "mobx-react-lite"
import {
  SearchContext,
  Search as SearchStore,
} from "#src/features/registration/stores/search"
import { Search } from "#src/features/registration/components/search/Search"
import { useEvents } from "#src/features/event/hooks"
import { useRegistrationStore } from "#src/features/registration/hooks"

export const SearchPage = observer(() => {
  const events = useEvents()
  const regStore = useRegistrationStore()
  const [firstEvent] = events
  const state = useLocalObservable(
    () => new SearchStore(regStore, firstEvent?.id),
  )

  return (
    <SearchContext.Provider value={state}>
      <Search
        events={Array.from(events, (e) => ({
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
