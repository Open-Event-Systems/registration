import { Title as PageTitle } from "#src/components/title/Title"
import { useParams } from "react-router-dom"
import {
  CardGrid,
  NoRegistrationsMessage,
} from "#src/features/selfservice/components/card/CardGrid"
import { Anchor, Box, Button, Grid } from "@mantine/core"
import { IconPlus } from "@tabler/icons-react"
import {
  RegistrationCard,
  RegistrationCardPlaceholder,
} from "#src/features/selfservice/components/card/RegistrationCard"
import { observer } from "mobx-react-lite"
import { useLocation, useNavigate } from "#src/hooks/location"
import {
  useCompleteCartInterviewFn,
  useCurrentCart,
  useSelfServiceAPI,
  useStartCartInterviewFn,
} from "#src/features/selfservice/hooks"
import {
  SelfServiceEvent,
  SelfServiceRegistrationResponse,
} from "#src/features/selfservice/types"
import { Link as RLink } from "react-router-dom"
import { InterviewOptionsDialog } from "#src/features/cart/components/interview/InterviewOptionsDialog"
import { InterviewDialog } from "#src/features/interview/components/InterviewDialog"
import { AccessCodeOptionsDialog } from "#src/features/selfservice/components/access-code/AccessCodeOptionsDialog"
import { Markdown } from "@open-event-systems/interview-components"

import { useQuery } from "@tanstack/react-query"

import classes from "./EventPage.module.css"

export const EventPage = () => {
  const { eventId = "", accessCode } = useParams()

  const selfServiceAPI = useSelfServiceAPI()
  const event = useQuery(selfServiceAPI.readEvent(eventId))

  const accessCodeResult = useQuery({
    ...selfServiceAPI.checkAccessCode(eventId, accessCode || ""),
    enabled: !!accessCode,
  })

  const registrations = useQuery(
    selfServiceAPI.listRegistrations({
      eventId: eventId,
      accessCode: accessCode,
    }),
  )

  const currentCartQuery = useCurrentCart(eventId)
  const completeInterview = useCompleteCartInterviewFn()

  const loc = useLocation()
  const navigate = useNavigate()

  if (!event.isSuccess || !registrations.isSuccess || !currentCartQuery.data) {
    return (
      <CardGrid>
        <RegistrationCardPlaceholder />
        <RegistrationCardPlaceholder />
        <RegistrationCardPlaceholder />
      </CardGrid>
    )
  }

  const [currentCartId, currentCart] = currentCartQuery.data

  return (
    <PageTitle title={event.data.name}>
      <RegistrationsView
        event={event.data}
        currentCartId={currentCartId}
        registrations={registrations.data.registrations}
      />
      {/* Spacer only for small screens */}
      <Box className={classes.spacer} />
      {registrations.data.add_options.length > 0 && (
        <Grid align="center" className={classes.grid}>
          <Grid.Col
            span={{
              base: 12,
              sm: "content",
            }}
          >
            <Button
              variant="filled"
              leftSection={<IconPlus />}
              fullWidth
              onClick={() => {
                // show dialog
                navigate(loc, {
                  state: {
                    ...loc.state,
                    showInterviewOptionsDialog: {
                      eventId: eventId,
                      cartId: currentCartId,
                    },
                  },
                })
              }}
            >
              Add Registration
            </Button>
          </Grid.Col>
          {currentCart.registrations.length > 0 ? (
            <Grid.Col span="content">
              <Anchor component={RLink} to={`/events/${eventId}/cart`}>
                View cart ({currentCart.registrations.length})
              </Anchor>
            </Grid.Col>
          ) : null}
        </Grid>
      )}
      <InterviewOptionsDialog.Manager
        options={registrations.data.add_options}
      />
      <AccessCodeOptionsDialog.Manager
        eventId={eventId}
        cartId={currentCartId}
        opened={
          accessCodeResult.isSuccess && !loc.state?.showInterviewDialog?.eventId
        }
        accessCode={accessCode}
        response={registrations.data}
      />
      <InterviewDialog.Manager onComplete={completeInterview} />
    </PageTitle>
  )
}

const RegistrationsView = observer(
  ({
    event,
    registrations,
    currentCartId,
  }: {
    event: SelfServiceEvent
    registrations: SelfServiceRegistrationResponse[]
    currentCartId: string
  }) => {
    const startInterview = useStartCartInterviewFn(currentCartId, event.id)

    if (registrations.length == 0) {
      return <NoRegistrationsMessage className={classes.noRegMessage} />
    } else {
      return (
        <CardGrid className={classes.cardGrid}>
          {registrations.map((r) => (
            <RegistrationCard
              key={r.registration.id}
              title={r.registration.title}
              subtitle={r.registration.subtitle}
              menuOptions={r.change_options.map((o) => ({
                id: o.id,
                label: o.name,
              }))}
              onMenuSelect={async (id) => {
                await startInterview(id, { registrationId: r.registration.id })
              }}
            >
              <Markdown content={r.registration.description} />
            </RegistrationCard>
          ))}
        </CardGrid>
      )
    }
  },
)

RegistrationsView.displayName = "RegistrationsView"
