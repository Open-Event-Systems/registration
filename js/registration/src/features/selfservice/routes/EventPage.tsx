import { Title as PageTitle, Subtitle } from "#src/components/title/Title"
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
  useAccessCodeLoader,
  useSelfServiceLoader,
} from "#src/features/selfservice/hooks"
import { Event } from "#src/features/event/types"
import { SelfServiceRegistrationResponse } from "#src/features/selfservice/types"
import { fetchCartInterview } from "#src/features/cart/api"
import { useWretch } from "#src/hooks/api"
import {
  fetchCurrentOrEmptyCart,
  getCurrentCartId,
} from "#src/features/cart/utils"
import { useEvents } from "#src/features/event/hooks"
import { useCurrentCartStore } from "#src/features/cart/hooks"
import { Link as RLink } from "react-router-dom"
import { InterviewOptionsDialog } from "#src/features/cart/components/interview/InterviewOptionsDialog"
import { InterviewDialog } from "#src/features/interview/components/InterviewDialog"
import { Cart } from "#src/features/cart/types"
import { AccessCodeOptionsDialog } from "#src/features/selfservice/components/access-code/AccessCodeOptionsDialog"
import { Markdown } from "@open-event-systems/interview-components"
import { useInterviewRecordStore } from "#src/features/interview/hooks"
import { defaultAPI, startInterview } from "@open-event-systems/interview-lib"

import classes from "./EventPage.module.css"

export const EventPage = () => {
  const { eventId = "", accessCode = "" } = useParams()
  const events = useEvents()
  const event = events.getEvent(eventId) as Event
  const selfService = useSelfServiceLoader()
  const currentCartStore = useCurrentCartStore()
  const accessCodeLoader = useAccessCodeLoader()

  const wretch = useWretch()
  const loc = useLocation()
  const navigate = useNavigate()

  return (
    <PageTitle title={event.name}>
      <Subtitle subtitle="Manage registrations">
        <selfService.Component
          placeholder={
            <CardGrid>
              <RegistrationCardPlaceholder />
              <RegistrationCardPlaceholder />
              <RegistrationCardPlaceholder />
            </CardGrid>
          }
        >
          {(results) => {
            return (
              <>
                <RegistrationsView
                  event={event}
                  registrations={results.registrations}
                />
                {/* Spacer only for small screens */}
                <Box className={classes.spacer} />
                {results.add_options.length > 0 && (
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
                              showInterviewOptionsDialog: eventId,
                            },
                          })
                        }}
                      >
                        Add Registration
                      </Button>
                    </Grid.Col>
                    {currentCartStore.loader?.value?.registrations.length ? (
                      <Grid.Col span="content">
                        <Anchor
                          component={RLink}
                          to={`/events/${eventId}/cart`}
                        >
                          View cart (
                          {currentCartStore.loader.value.registrations.length})
                        </Anchor>
                      </Grid.Col>
                    ) : null}
                  </Grid>
                )}
                <InterviewOptionsDialog.Manager options={results.add_options} />
                <AccessCodeOptionsDialog.Manager
                  opened={
                    !!accessCodeLoader.value &&
                    !loc.state?.showInterviewDialog?.eventId
                  }
                  accessCode={accessCode}
                  response={results}
                />
                <InterviewDialog.Manager
                  onComplete={async (record) => {
                    const response = record.stateResponse
                    const metadata = record.metadata

                    if (
                      metadata.cartId &&
                      metadata.eventId &&
                      response.complete &&
                      response.target_url
                    ) {
                      const res = await wretch
                        .url(response.target_url, true)
                        .json({ state: response.state })
                        .post()
                        .res()

                      const cart: Cart = await res.json()

                      const url = new URL(res.url)
                      const parts = url.pathname.split("/")
                      const newCartId = parts[parts.length - 1]
                      currentCartStore.setCurrentCart(newCartId, cart)
                      navigate(loc, {
                        state: { ...loc.state, showInterviewDialog: undefined },
                        replace: true,
                      })
                      navigate(`/events/${metadata.eventId}/cart`)
                    }
                  }}
                />
              </>
            )
          }}
        </selfService.Component>
      </Subtitle>
    </PageTitle>
  )
}

const RegistrationsView = observer(
  ({
    event,
    registrations,
  }: {
    event: Event
    registrations: SelfServiceRegistrationResponse[]
  }) => {
    const navigate = useNavigate()
    const loc = useLocation()
    const wretch = useWretch()
    const interviewRecordStore = useInterviewRecordStore()

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
                let cartId = getCurrentCartId()
                if (!cartId) {
                  const [curOrEmptyCartId] = await fetchCurrentOrEmptyCart(
                    wretch,
                    event.id,
                  )
                  cartId = curOrEmptyCartId
                }

                const state = await fetchCartInterview(
                  wretch,
                  cartId,
                  id,
                  r.registration.id,
                )

                const next = await startInterview(
                  interviewRecordStore,
                  defaultAPI,
                  state,
                  {
                    cartId: cartId,
                    eventId: event.id,
                  },
                )

                // show dialog
                navigate(loc, {
                  state: {
                    ...loc.state,
                    showInterviewDialog: {
                      eventId: event.id,
                      recordId: next.id,
                    },
                  },
                })
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
