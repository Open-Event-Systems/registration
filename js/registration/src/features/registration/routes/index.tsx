import {
  LoadingOverlay,
  ShowLoadingOverlay,
  SimpleLayout,
  Subtitle,
  Title,
} from "#src/components"
import { AuthContext } from "#src/features/auth/hooks"
import { Await, Loader, createLoader, useLoader } from "#src/features/loader"
import { WretchContext } from "#src/hooks/api"
import { AppStoreContext } from "#src/hooks/app"
import { AppStore } from "#src/stores/AppStore"
import { makeApp } from "#src/util/react"
import { MantineProvider } from "@mantine/core"
import {
  Outlet,
  RouterProvider,
  createBrowserRouter,
  useParams,
} from "react-router-dom"

import { SignInDialog } from "#src/features/auth/components/dialog/SignInDialog"

import { createEventAPI } from "#src/features/event/api"
import { EventStore } from "#src/features/event/stores"
import { EventStoreContext } from "#src/features/event/hooks"
import { SearchPage } from "#src/features/registration/routes/SearchPage"
import "@mantine/core/styles.css"
import "@open-event-systems/interview-components/styles.css"
import "#src/components/styles.css"
import "#src/features/auth/styles.css"
import "#src/features/interview/styles.css"
import "#src/features/cart/styles.css"
import "#src/features/registration/components/search/Results.scss"
import "#src/features/registration/components/registration/fields/RegistrationFields.scss"
import theme from "#src/config/theme"
import { RegistrationPage } from "#src/features/registration/routes/RegistrationPage"
import { RegistrationStoreProvider } from "#src/features/registration"

const AppRoute = ({ app }: { app: Loader<AppStore> }) => {
  const setup = useLoader(async () => {
    const _app = await app
    const eventAPI = createEventAPI(_app.authStore.authWretch)
    const eventStore = new EventStore(eventAPI)
    await eventStore.load()

    return { eventStore }
  }, [app])

  return (
    <>
      <Await value={app} fallback={<ShowLoadingOverlay />}>
        {(app) => (
          <AppStoreContext.Provider value={app}>
            <AuthContext.Provider value={app.authStore}>
              <WretchContext.Provider value={app.authStore.authWretch}>
                <Await value={setup} fallback={<ShowLoadingOverlay />}>
                  {({ eventStore }) => (
                    <EventStoreContext.Provider value={eventStore}>
                      <RegistrationStoreProvider>
                        <Outlet />
                      </RegistrationStoreProvider>
                    </EventStoreContext.Provider>
                  )}
                </Await>
                <SignInDialog.Manager
                  authStore={app.authStore}
                  wretch={app.wretch}
                />
              </WretchContext.Provider>
            </AuthContext.Provider>
          </AppStoreContext.Provider>
        )}
      </Await>
      <LoadingOverlay />
    </>
  )
}

makeApp(() => {
  const appLoader = createLoader(async () => {
    const app = await AppStore.fromConfig()
    await app.authStore.load()
    return app
  })

  const router = createBrowserRouter(
    [
      {
        element: <AppRoute app={appLoader} />,
        children: [
          {
            Component() {
              return (
                <SimpleLayout>
                  <Title title="Registrations">
                    <Subtitle subtitle="Search registrations">
                      <Outlet />
                    </Subtitle>
                  </Title>
                </SimpleLayout>
              )
            },
            children: [
              {
                index: true,
                element: <SearchPage />,
              },
              {
                path: ":registrationId",
                Component() {
                  const { registrationId = "" } = useParams()
                  return <Outlet key={registrationId} />
                },
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
    {
      basename: "/registrations",
    },
  )

  return (
    <MantineProvider theme={theme}>
      <RouterProvider router={router} />
    </MantineProvider>
  )
})