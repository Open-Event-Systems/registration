import { UserMenu } from "#src/components"
import { useAuth } from "#src/features/auth/hooks"
import { Badge } from "#src/features/checkin/components/badge/Badge"
import { CheckinLayout } from "#src/features/checkin/components/layout/CheckinLayout"
import { Registration } from "#src/features/checkin/components/registration/Registration"
import { useEventAPI } from "#src/features/event/hooks"
import {
  InterviewContent,
  useInterviewRecordStore,
} from "#src/features/interview"
import { useRegistrationAPI } from "#src/features/registration/hooks"
import { useLocation, useNavigate } from "#src/hooks/location"
import { isAPIError } from "#src/utils/api"
import { Alert, Anchor, Box } from "@mantine/core"
import { defaultAPI, startInterview } from "@open-event-systems/interview-lib"
import { useMutation, useQuery } from "@tanstack/react-query"
import { useEffect } from "react"
import { Link, useParams } from "react-router-dom"

export const CheckinPage = () => {
  const { eventId = "", registrationId = "" } = useParams()

  const auth = useAuth()
  const loc = useLocation()
  const navigate = useNavigate()

  const interviewRecordStore = useInterviewRecordStore()

  const recordId = loc.state?.showInterviewRecord
  const curRecord = recordId
    ? interviewRecordStore.getRecord(recordId)
    : undefined

  const eventAPI = useEventAPI()
  const registrationAPI = useRegistrationAPI()
  const events = useQuery(eventAPI.list())
  const event = useQuery(eventAPI.read(eventId))

  const registration = useQuery({
    ...registrationAPI.read(registrationId),
    enabled: event.isSuccess,
  })

  const checkinInterview = useQuery({
    ...registrationAPI.readCheckinInterview(registrationId),
    enabled: event.isSuccess && !curRecord,
  })

  const completeCheckin = useMutation(
    registrationAPI.completeCheckinInterview(registrationId),
  )

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

  return (
    <>
      <CheckinLayout.Header>
        <Anchor component={Link} to={`/check-in/${eventId}`}>
          &laquo; Back
        </Anchor>
        <CheckinLayout.Spacer />
        <UserMenu
          username={auth.authInfo?.email || "Guest"}
          onSignOut={() => {
            auth.signOut()
          }}
        />
      </CheckinLayout.Header>
      <CheckinLayout.Left className="CheckinPage-left">
        {registration.isSuccess ? <Badge badgeUrl="/" /> : undefined}
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
            navigate(`/check-in/${eventId}`)
          }}
          onClose={() => {
            navigate(`/check-in/${eventId}`)
          }}
        />
      </CheckinLayout.Right>
    </>
  )
}
