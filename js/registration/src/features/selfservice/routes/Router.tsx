import { SimpleLayout } from "#src/components/layout/SimpleLayout.js"
import { Title } from "#src/components/title/Title.js"
import { SigninDialog } from "#src/features/auth/components/SigninDialog.js"
import { useAuth } from "#src/features/auth/hooks.js"
import { useCurrentCartStore } from "#src/features/cart/hooks.js"
import {
  CartStoreProvider,
  CurrentCartStoreProvider,
} from "#src/features/cart/providers.js"
import { useEvents } from "#src/features/event/hooks.js"
import { EventStoreProvider } from "#src/features/event/providers.js"
import { InterviewStateStoreProvider } from "#src/features/interview/routes.js"
import {
  checkAccessCode,
  listSelfServiceRegistrations,
} from "#src/features/selfservice/api.js"
import {
  AccessCodeLoaderContext,
  SelfServiceLoaderContext,
  useAccessCodeLoader,
} from "#src/features/selfservice/hooks.js"
import { CartPage } from "#src/features/selfservice/routes/CartPage.js"
import { EventPage } from "#src/features/selfservice/routes/EventPage.js"
import { useWretch } from "#src/hooks/api.js"
import { useLoader } from "#src/hooks/loader.js"
import { AppRoute } from "#src/routes/AppRoute.js"
import {
  LoadingOverlay,
  ShowLoadingOverlay,
} from "#src/routes/LoadingOverlay.js"
import { NotFoundPage } from "#src/routes/NotFoundPage.js"
import { NotFoundError } from "#src/util/loader.js"
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
      : Promise.reject(new NotFoundError())
  )
  const selfServiceLoader = useLoader(() =>
    listSelfServiceRegistrations(wretch, eventId, accessCode)
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
    <SigninDialog.Manager wretch={authStore.wretch} authStore={authStore}>
      <InterviewStateStoreProvider>
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
      </InterviewStateStoreProvider>
    </SigninDialog.Manager>
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
