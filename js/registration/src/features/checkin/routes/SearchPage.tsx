import { CheckinLayout } from "#src/features/checkin/components/layout/CheckinLayout"
import { Search } from "#src/features/checkin/components/search/Search"
import { useCheckInStore } from "#src/features/checkin/hooks"
import { useEventAPI } from "#src/features/event/hooks"
import { useQueueAPI } from "#src/features/queue/hooks"
import { useRegistrationAPI } from "#src/features/registration/hooks"
import { useNavigate } from "#src/hooks/location"
import { Box } from "@mantine/core"
import { useMutation, useQuery } from "@tanstack/react-query"
import { action } from "mobx"
import { observer, useLocalObservable } from "mobx-react-lite"
import { useEffect } from "react"
import { useParams } from "react-router-dom"

export const SearchPage = observer(() => {
  const { eventId = "" } = useParams()
  const eventAPI = useEventAPI()
  const navigate = useNavigate()

  const checkInStore = useCheckInStore()
  const queueAPI = useQueueAPI()

  const event = useQuery(eventAPI.read(eventId))

  const registrationAPI = useRegistrationAPI()
  const state = useLocalObservable(() => ({
    query: "",
    throttled: "",
  }))

  const { query, throttled } = state

  const search = useQuery({
    queryKey: [
      "registrations",
      { query: throttled.trim(), eventId: event.data?.id },
    ],
    queryFn: registrationAPI.list(throttled.trim(), {
      event_id: event.data?.id,
    }).queryFn,
    placeholderData(prev) {
      return !!throttled.trim() ? prev : undefined
    },
    enabled: !!throttled.trim() && !!event.data?.id,
  })

  useEffect(() => {
    const timeout = window.setTimeout(
      action(() => {
        state.throttled = query
      }),
      250,
    )

    return () => {
      window.clearTimeout(timeout)
    }
  }, [query])

  const removeItem = useMutation(queueAPI.cancelQueueItem())

  return (
    <>
      <CheckinLayout.Header />
      <CheckinLayout.Body>
        <Box
          component="form"
          onSubmit={(e) => {
            e.preventDefault()
            if (
              state.query.trim() == state.throttled.trim() &&
              search.isSuccess &&
              search.data.length == 1
            ) {
              navigate(
                `/check-in/${eventId}/registrations/${search.data[0].id}`,
              )
            }
          }}
        >
          <Search
            query={query}
            onChange={action((q) => (state.query = q))}
            registrations={search.data}
            onSelect={(id) => {
              navigate(`/check-in/${eventId}/registrations/${id}`)
            }}
            nextInLine={checkInStore.queueItems}
            onSelectNextInLine={(item) => {
              if (item.registration_id) {
                navigate(
                  `/check-in/${eventId}/registrations/${item.registration_id}`,
                )
              }
            }}
            onRemoveNextInLine={action((item) => {
              removeItem.mutate(item.id)
              checkInStore.queueItems = checkInStore.queueItems.filter(
                (it) => it.id != item.id,
              )
            })}
          />
          <input type="submit" style={{ display: "none" }} />
        </Box>
      </CheckinLayout.Body>
    </>
  )
})
