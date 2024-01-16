import { Badge } from "#src/features/checkin/components/badge/Badge"
import { CheckinLayout } from "#src/features/checkin/components/layout/CheckinLayout"
import { Registration } from "#src/features/checkin/components/registration/Registration"
import { useCheckInStore } from "#src/features/checkin/hooks"
import { useEventAPI } from "#src/features/event/hooks"
import {
  InterviewContent,
  useInterviewRecordStore,
} from "#src/features/interview"
import { useQueueAPI } from "#src/features/queue/hooks"
import { useRegistrationAPI } from "#src/features/registration/hooks"
import { useLocation, useNavigate } from "#src/hooks/location"
import { isAPIError } from "#src/utils/api"
import { Alert, Anchor, Box } from "@mantine/core"
import { defaultAPI, startInterview } from "@open-event-systems/interview-lib"
import { useMutation, useQuery } from "@tanstack/react-query"
import { action, runInAction } from "mobx"
import { observer } from "mobx-react-lite"
import { useEffect, useRef } from "react"
import { Link, useParams } from "react-router-dom"

export const CheckinPage = observer(() => {
  const { eventId = "", registrationId = "" } = useParams()

  const loc = useLocation()
  const navigate = useNavigate()
  const queueItemId = loc.state?.checkInQueueItemId

  const interviewRecordStore = useInterviewRecordStore()

  const recordId = loc.state?.showInterviewRecord
  const curRecord = recordId
    ? interviewRecordStore.getRecord(recordId)
    : undefined

  const eventAPI = useEventAPI()
  const registrationAPI = useRegistrationAPI()
  const events = useQuery(eventAPI.list())
  const event = useQuery(eventAPI.read(eventId))

  const checkInStore = useCheckInStore()
  const queueAPI = useQueueAPI()

  const registration = useQuery({
    ...registrationAPI.read(registrationId),
    enabled: event.isSuccess,
  })

  const checkinInterview = useQuery({
    ...registrationAPI.readCheckinInterview(
      registrationId,
      checkInStore.stationId ?? undefined,
    ),
    enabled: event.isSuccess,
  })

  const completeCheckin = useMutation(
    registrationAPI.completeCheckinInterview(registrationId),
  )

  const completeItem = useMutation(queueAPI.completeQueueItem())
  const cancelItem = useMutation(queueAPI.cancelQueueItem())
  const logItem = useMutation(queueAPI.logQueueItem())
  const successRef = useRef<boolean>(false)

  useEffect(() => {
    if (checkinInterview.isSuccess && !curRecord) {
      startInterview(
        interviewRecordStore,
        defaultAPI,
        checkinInterview.data,
      ).then((record) => {
        navigate(loc, {
          state: { ...loc.state, showInterviewRecord: record.id },
          replace: true,
        })
      })
    }
  }, [checkinInterview.isSuccess, recordId])

  useEffect(() => {
    return action(() => {
      if (!successRef.current && queueItemId) {
        cancelItem.mutate(queueItemId)
      }
    })
  }, [queueItemId])

  return (
    <>
      <CheckinLayout.Header>
        <Anchor component={Link} to={`/check-in/${eventId}`}>
          &laquo; Back
        </Anchor>
      </CheckinLayout.Header>
      <CheckinLayout.Left className="CheckinPage-left">
        {event.data && registration.isSuccess ? (
          <Badge
            badgeUrl={event.data.badge_url}
            badgeData={registration.data}
          />
        ) : undefined}
      </CheckinLayout.Left>
      <CheckinLayout.Center className="CheckinPage-center">
        {registration.isSuccess ? (
          <Box>
            <Registration
              registration={registration.data}
              eventsMap={events.data}
            />
          </Box>
        ) : undefined}
      </CheckinLayout.Center>
      <CheckinLayout.Right className="CheckinPage-right">
        <Box>
          {completeCheckin.isError && (
            <Alert color="red">
              {isAPIError(completeCheckin.error)
                ? completeCheckin.error.json.detail
                : completeCheckin.error.message}
            </Alert>
          )}
        </Box>
        <InterviewContent.Manager
          onComplete={async (record) => {
            completeCheckin.reset()
            await completeCheckin.mutateAsync(record)
            successRef.current = true
            runInAction(() => {
              if (queueItemId) {
                completeItem.mutate({
                  itemId: queueItemId,
                  registrationId: registration.data?.id,
                })
              } else {
                if (checkInStore.stationId && loc.state?.checkInStartTime) {
                  logItem.mutate({
                    station_id: checkInStore.stationId,
                    registration_id: registrationId,
                    date_started: loc.state?.checkInStartTime,
                  })
                }
              }
            })
            navigate(`/check-in/${eventId}`)
          }}
          onClose={() => {
            navigate(`/check-in/${eventId}`)
          }}
        />
      </CheckinLayout.Right>
    </>
  )
})

CheckinPage.displayName = "CheckinPage"
