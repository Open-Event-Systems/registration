import { LoadingOverlay, ShowLoadingOverlay } from "#src/components"
import { SimpleLayout } from "#src/components/layout/SimpleLayout"
import { Title } from "#src/components/title/Title"
import { SignInDialog } from "#src/features/auth/components/dialog/SignInDialog"
import { useAuth } from "#src/features/auth/hooks"
import { useCurrentCartStore } from "#src/features/cart/hooks"
import {
  CartStoreProvider,
  CurrentCartStoreProvider,
} from "#src/features/cart/providers"
import { useEvents } from "#src/features/event/hooks"
import { EventStoreProvider } from "#src/features/event/providers"
import { InterviewRecordStoreProvider } from "#src/features/interview/providers"
import {
  checkAccessCode,
  listSelfServiceRegistrations,
} from "#src/features/selfservice/api"
import {
  AccessCodeLoaderContext,
  SelfServiceLoaderContext,
  useAccessCodeLoader,
} from "#src/features/selfservice/hooks"
import { CartPage } from "#src/features/selfservice/routes/CartPage"
import { EventPage } from "#src/features/selfservice/routes/EventPage"
import { useWretch } from "#src/hooks/api"
import { useLoader } from "#src/hooks/loader"
import { AppRoute } from "#src/routes/AppRoute"
import { NotFoundPage } from "#src/routes/NotFoundPage"
import { NotFoundError } from "#src/util/loader"
import { Text } from "@mantine/core"
import { Fragment, ReactNode } from "react"
import { Outlet, createBrowserRouter, useParams } from "react-router-dom"

const LayoutRoute = () => (
  <>
    <SimpleLayout>
      <Outlet />
    </SimpleLayout>
    <LoadingOverlay />
  </>
)

const SelfServiceLoader = ({
  children,
  eventId,
  accessCode,
}: {
  children?: ReactNode
  eventId: string
  accessCode?: string
}) => {
  const wretch = useWretch()
  const eventStore = useEvents()
  const currentCartStore = useCurrentCartStore()
  const accessCodeLoader = useLoader(() =>
    accessCode
      ? checkAccessCode(wretch, eventId, accessCode)
      : Promise.reject(new NotFoundError()),
  )
  const selfServiceLoader = useLoader(() =>
    listSelfServiceRegistrations(wretch, eventId, accessCode),
  )

  const loader = useLoader(async () => {
    const event = await eventStore.load(eventId)
    if (!event) {
      return null
    }
    await currentCartStore.checkAndSetCurrentCart()
    return true
  })

  return (
    <loader.Component
      placeholder={<ShowLoadingOverlay />}
      notFound={<NotFoundPage />}
    >
      <AccessCodeLoaderContext.Provider value={accessCodeLoader}>
        <SelfServiceLoaderContext.Provider value={selfServiceLoader}>
          {children}
        </SelfServiceLoaderContext.Provider>
      </AccessCodeLoaderContext.Provider>
    </loader.Component>
  )
}

const SelfServiceAppRoute = () => {
  const { eventId = "", accessCode = "" } = useParams()
  const authStore = useAuth()
  return (
    <SignInDialog.Manager wretch={authStore.wretch} authStore={authStore}>
      <InterviewRecordStoreProvider>
        <EventStoreProvider>
          <CartStoreProvider>
            <Fragment key={eventId}>
              <Fragment key={accessCode}>
                <CurrentCartStoreProvider eventId={eventId}>
                  <SelfServiceLoader eventId={eventId} accessCode={accessCode}>
                    <Outlet />
                  </SelfServiceLoader>
                </CurrentCartStoreProvider>
              </Fragment>
            </Fragment>
          </CartStoreProvider>
        </EventStoreProvider>
      </InterviewRecordStoreProvider>
    </SignInDialog.Manager>
  )
}

const AccessCodeRoute = () => {
  const loader = useAccessCodeLoader()
  return (
    <loader.Component
      placeholder={<ShowLoadingOverlay />}
      notFound={<AccessCodeNotFoundPage />}
    >
      <Outlet />
    </loader.Component>
  )
}

const AccessCodeNotFoundPage = () => (
  <Title title="Access Code Not Found">
    <Text component="p">
      The access code was not found. It may be invalid or expired.
    </Text>
  </Title>
)

export const router = createBrowserRouter([
  {
    element: <AppRoute />,
    children: [
      {
        element: <LayoutRoute />,
        children: [
          {
            element: <SelfServiceAppRoute />,
            children: [
              {
                path: "/events/:eventId",
                element: <EventPage />,
              },
              {
                element: <AccessCodeRoute />,
                children: [
                  {
                    path: "/events/:eventId/access-code/:accessCode",
                    element: <EventPage />,
                  },
                ],
              },
              {
                path: "/events/:eventId/cart",
                element: <CartPage />,
              },
            ],
          },
        ],
      },
    ],
  },
  {
    path: "*",
    element: (
      <SimpleLayout>
        <NotFoundPage />
      </SimpleLayout>
    ),
  },
])
