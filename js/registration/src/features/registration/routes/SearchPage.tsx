import { observer, useLocalObservable } from "mobx-react-lite"
import {
  SearchContext,
  Search as SearchStore,
} from "#src/features/registration/stores/search"
import { Search } from "#src/features/registration/components/search/Search"
import { EventAPIContext } from "#src/features/event/hooks"
import { RegistrationAPIContext } from "#src/features/registration/hooks"
import {
  useInfiniteQuery,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query"
import { useContext, useState } from "react"
import { Group, Select } from "@mantine/core"
import {
  InterviewDialog,
  useInterviewRecordStore,
} from "#src/features/interview"
import { useLocation, useNavigate } from "#src/hooks/location"
import { defaultAPI, startInterview } from "@open-event-systems/interview-lib"
import { useWretch } from "#src/hooks/api"
import { Registration } from "#src/features/registration"

export const SearchPage = observer(() => {
  const eventAPI = useContext(EventAPIContext)
  const registrationAPI = useContext(RegistrationAPIContext)
  const events = useQuery(eventAPI.list())

  const wretch = useWretch()
  const loc = useLocation()
  const navigate = useNavigate()
  const interviewStore = useInterviewRecordStore()

  const [firstEvent] = events.data.values()
  const state = useLocalObservable(
    () => new SearchStore(registrationAPI, firstEvent?.id),
  )

  const [addEvent, setAddEvent] = useState(firstEvent ? firstEvent.id : null)

  const client = useQueryClient()
  const addInterviewsQuery = useQuery({
    ...registrationAPI.listAddInterviews(addEvent ?? ""),
    enabled: !!addEvent,
  })

  const { data, hasNextPage, fetchNextPage } = useInfiniteQuery(
    state.queryOptions,
  )

  return (
    <>
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
      <Group>
        <Select
          value={addEvent}
          onChange={(e) => {
            setAddEvent(e)
          }}
          data={Array.from(events.data.values(), (e) => ({
            label: e.name,
            value: e.id,
          }))}
        />
        <Select
          placeholder="Add registration..."
          value={null}
          onChange={async (id) => {
            if (!addEvent || !id) {
              return
            }

            const response = await client.ensureQueryData(
              registrationAPI.readAddInterview(addEvent, id),
            )
            const record = await startInterview(
              interviewStore,
              defaultAPI,
              response,
              {
                eventId: addEvent,
              },
            )
            navigate(loc, {
              state: {
                ...loc.state,
                showInterviewDialog: { recordId: record.id },
              },
            })
          }}
          data={
            addEvent && addInterviewsQuery.isSuccess
              ? addInterviewsQuery.data.map((opt) => ({
                  label: opt.name,
                  value: opt.id,
                }))
              : []
          }
        />
      </Group>
      <InterviewDialog.Manager
        onComplete={async (r) => {
          const response = r.stateResponse
          if (response.complete && response.target_url && r.metadata.eventId) {
            const res = await wretch
              .url(response.target_url, true)
              .json({ state: response.state })
              .post()
              .json<Registration>()

            navigate(loc, {
              state: { ...loc.state, showInterviewDialog: undefined },
            })
            navigate(`/registrations/${res.id}`)
          }
        }}
      />
    </>
  )
})

const flatten = <T,>(data: T[][]): T[] => {
  const flattened = []
  for (const page of data) {
    flattened.push(...page)
  }
  return flattened
}
