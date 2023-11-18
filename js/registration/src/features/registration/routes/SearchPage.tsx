import { Subtitle, Title } from "#src/components"
import { useRegistrationAPI } from "#src/features/registration"
import { observer, useLocalObservable } from "mobx-react-lite"
import {
  SearchContext,
  Search as SearchStore,
} from "#src/features/registration/stores/search"
import { Search } from "#src/features/registration/components/search/Search"
import { useEvents } from "#src/features/event/hooks"
import { Event } from "#src/features/event/types"

export const SearchPage = () => {
  const events = useEvents()
  return (
    <Title title="Registrations">
      <Subtitle subtitle="Search registrations">
        <events.loader.Component>
          {(events) => <SearchPageContent events={events} />}
        </events.loader.Component>
      </Subtitle>
    </Title>
  )
}

const SearchPageContent = observer(
  ({ events }: { events: Map<string, Event> }) => {
    const api = useRegistrationAPI()
    const state = useLocalObservable(
      () => new SearchStore(api, Array.from(events.keys())[0] ?? null),
    )

    return (
      <SearchContext.Provider value={state}>
        <Search
          events={Array.from(events.values(), (e) => ({
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
  },
)
