import {
  LoadingOverlay,
  ShowLoadingOverlay,
  SimpleLayout,
} from "#src/components"
import { SignInDialog } from "#src/features/auth/components/dialog/SignInDialog"
import { useAuth } from "#src/features/auth/hooks"
import { useEvents } from "#src/features/event/hooks"
import { EventStoreProvider } from "#src/features/event/providers"
import {
  RegistrationAPIProvider,
  RegistrationProvider,
} from "#src/features/registration"
import { RegistrationPage } from "#src/features/registration/routes/RegistrationPage"
import { SearchPage } from "#src/features/registration/routes/SearchPage"
import { AppRoute } from "#src/routes/AppRoute"
import { NotFoundPage } from "#src/routes/NotFoundPage"
import { Outlet, createBrowserRouter, useParams } from "react-router-dom"

const LayoutRoute = () => (
  <>
    <SimpleLayout>
      <Outlet />
    </SimpleLayout>
    <LoadingOverlay />
  </>
)

const RegistrationsRoute = () => {
  const auth = useAuth()
  return (
    <SignInDialog.Manager wretch={auth.wretch} authStore={auth}>
      <EventStoreProvider>
        <RegistrationAPIProvider>
          <Outlet />
        </RegistrationAPIProvider>
      </EventStoreProvider>
    </SignInDialog.Manager>
  )
}

const LoadingRoute = () => {
  const events = useEvents()
  return (
    <events.loader.Component placeholder={<ShowLoadingOverlay />}>
      <Outlet />
    </events.loader.Component>
  )
}

const RegistrationRoute = () => {
  const { registrationId = "" } = useParams()
  return (
    <RegistrationProvider id={registrationId}>
      <Outlet />
    </RegistrationProvider>
  )
}

export const router = createBrowserRouter(
  [
    {
      element: <AppRoute />,
      children: [
        {
          element: <LayoutRoute />,
          children: [
            {
              element: <RegistrationsRoute />,
              children: [
                {
                  element: <LoadingRoute />,
                  children: [
                    {
                      index: true,
                      element: <SearchPage />,
                    },
                    {
                      element: <RegistrationRoute />,
                      path: ":registrationId",
                      children: [
                        {
                          index: true,
                          element: <RegistrationPage />,
                        },
                      ],
                    },
                  ],
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
  ],
  {
    basename: "/registrations",
  },
)
