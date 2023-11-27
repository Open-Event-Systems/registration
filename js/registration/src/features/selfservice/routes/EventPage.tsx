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
  useSelfServiceAPI,
  useSelfServiceLoader,
} from "#src/features/selfservice/hooks"
import { Event } from "#src/features/event/types"
import {
  SelfServiceEvent,
  SelfServiceRegistrationResponse,
} from "#src/features/selfservice/types"
import {
  fetchCartInterview,
  getCartIdFromResponse,
} from "#src/features/cart/api"
import { useWretch } from "#src/hooks/api"
import {
  fetchCurrentOrEmptyCart,
  getCurrentCartId,
} from "#src/features/cart/utils"
import { useEvents } from "#src/features/event/hooks"
import { useCartAPI, useCurrentCartStore } from "#src/features/cart/hooks"
import { Link as RLink } from "react-router-dom"
import { InterviewOptionsDialog } from "#src/features/cart/components/interview/InterviewOptionsDialog"
import { InterviewDialog } from "#src/features/interview/components/InterviewDialog"
import { Cart } from "#src/features/cart/types"
import { AccessCodeOptionsDialog } from "#src/features/selfservice/components/access-code/AccessCodeOptionsDialog"
import { Markdown } from "@open-event-systems/interview-components"
import { useInterviewRecordStore } from "#src/features/interview/hooks"
import { defaultAPI, startInterview } from "@open-event-systems/interview-lib"

import classes from "./EventPage.module.css"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { NotFoundError } from "#src/features/loader"
import { useEffect } from "react"
import { isWretchError } from "#src/util/api"

export const EventPage = () => {
  const { eventId = "", accessCode = "" } = useParams()

  const client = useQueryClient()
  const cartAPI = useCartAPI()
  const selfServiceAPI = useSelfServiceAPI()
  const events = useQuery(selfServiceAPI.listEvents())
  const event = events.data.get(eventId)

  const registrations = useQuery(
    selfServiceAPI.listRegistrations({
      eventId: eventId,
      accessCode: accessCode,
    }),
  )

  const currentCart = useQuery({
    ...cartAPI.readCurrentCart(eventId),
    throwOnError: false,
  })

  const currentCartFailed =
    (currentCart.isError &&
      isWretchError(currentCart.error) &&
      currentCart.error.status == 404) ||
    (currentCart.isSuccess && currentCart.data == null)

  const emptyCart = useQuery({
    ...cartAPI.readEmptyCart(eventId),
    enabled: currentCartFailed,
  })
  const setCurrentCart = useMutation(cartAPI.setCurrentCart(eventId))

  // replace current cart with empty cart if not found
  useEffect(() => {
    if (currentCartFailed && emptyCart.data) {
      setCurrentCart.mutate(emptyCart.data)
    }
  }, [currentCartFailed, emptyCart.data])

  // const events = useEvents()
  // const event = events.getEvent(eventId) as Event
  // const selfService = useSelfServiceLoader()
  // const currentCartStore = useCurrentCartStore()
  // const accessCodeLoader = useAccessCodeLoader()

  const wretch = useWretch()
  const loc = useLocation()
  const navigate = useNavigate()

  if (!registrations.isSuccess || !currentCart.data) {
    return (
      <CardGrid>
        <RegistrationCardPlaceholder />
        <RegistrationCardPlaceholder />
        <RegistrationCardPlaceholder />
      </CardGrid>
    )
  }

  if (!event) {
    // TODO: move where this error is defined, and catch it in a boundary
    throw new NotFoundError()
  }

  const currentCartId = currentCart.data[0]

  return (
    <PageTitle title={event.name}>
      <RegistrationsView
        event={event}
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
          {currentCart.data[1].registrations.length > 0 ? (
            <Grid.Col span="content">
              <Anchor component={RLink} to={`/events/${eventId}/cart`}>
                View cart ({currentCart.data[1].registrations.length})
              </Anchor>
            </Grid.Col>
          ) : null}
        </Grid>
      )}
      <InterviewOptionsDialog.Manager
        options={registrations.data.add_options}
      />
      {/* <AccessCodeOptionsDialog.Manager
        opened={
          !!accessCodeLoader.value &&
          !loc.state?.showInterviewDialog?.eventId
        }
        accessCode={accessCode}
        response={results}
      /> */}
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

            const newCartId = getCartIdFromResponse(res)
            const cart: Cart = await res.json()
            client.setQueryData(cartAPI.readCart(newCartId).queryKey, [
              newCartId,
              cart,
            ])
            setCurrentCart.mutate([newCartId, cart])
            navigate(loc, {
              state: { ...loc.state, showInterviewDialog: undefined },
              replace: true,
            })
            navigate(`/events/${metadata.eventId}/cart`)
          }
        }}
      />
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
    const navigate = useNavigate()
    const loc = useLocation()
    const client = useQueryClient()
    const interviewRecordStore = useInterviewRecordStore()

    const cartAPI = useCartAPI()

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
                const state = await client.ensureQueryData(
                  cartAPI.readAddInterview(currentCartId, id, {
                    registrationId: r.registration.id,
                  }),
                )

                const next = await startInterview(
                  interviewRecordStore,
                  defaultAPI,
                  state,
                  {
                    cartId: currentCartId,
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
