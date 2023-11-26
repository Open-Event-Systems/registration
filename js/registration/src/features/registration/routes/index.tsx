import {
  LoadingOverlay,
  ShowLoadingOverlay,
  SimpleLayout,
  Subtitle,
  Title,
} from "#src/components"
import { LoadingOverlay as MantineLoadingOverlay } from "@mantine/core"
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
  useLoaderData,
  useParams,
  useRouteError,
} from "react-router-dom"

import { SignInDialog } from "#src/features/auth/components/dialog/SignInDialog"

import { createEventAPI } from "#src/features/event/api"
import { EventStore } from "#src/features/event/stores"
import { EventAPIContext, EventStoreContext } from "#src/features/event/hooks"
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
import {
  QueryClient,
  QueryClientProvider,
  QueryErrorResetBoundary,
} from "@tanstack/react-query"
import { eventsRoute } from "#src/features/event/routes"
import { Suspense, useEffect, useState } from "react"
import { useLocation, useNavigate } from "#src/hooks/location"
import { isWretchError } from "#src/util/api"
import { createRegistrationAPI } from "#src/features/registration/api"
import { RegistrationAPIContext } from "#src/features/registration/hooks"

makeApp(() => {
  const appPromise = AppStore.fromConfig().then(async (app) => {
    await app.authStore.load()
    const wretch = app.wretch
    const authWretch = app.authStore.authWretch
    const eventAPI = createEventAPI(authWretch)
    const registrationAPI = createRegistrationAPI(authWretch)
    return {
      app,
      wretch,
      authWretch,
      eventAPI,
      registrationAPI,
    }
  })

  const eventAPI = appPromise.then((res) => res.eventAPI)
  const client = new QueryClient()

  const router = createBrowserRouter(
    [
      {
        id: "root",
        async loader() {
          return await appPromise
        },
        Component() {
          const { app, eventAPI, registrationAPI } = useLoaderData() as Awaited<
            typeof appPromise
          >
          return (
            <>
              <AppStoreContext.Provider value={app}>
                <AuthContext.Provider value={app.authStore}>
                  <WretchContext.Provider value={app.authStore.authWretch}>
                    <QueryClientProvider client={client}>
                      <EventAPIContext.Provider value={eventAPI}>
                        <RegistrationAPIContext.Provider
                          value={registrationAPI}
                        >
                          <Outlet />
                        </RegistrationAPIContext.Provider>
                      </EventAPIContext.Provider>
                      <SignInDialog.Manager
                        authStore={app.authStore}
                        wretch={app.wretch}
                      />
                    </QueryClientProvider>
                  </WretchContext.Provider>
                </AuthContext.Provider>
              </AppStoreContext.Provider>
            </>
          )
        },
        children: [
          {
            ErrorBoundary() {
              const err = useRouteError()
              if (isWretchError(err) && err.status == 401) {
                if (err.status == 401) {
                  return <ShowLoadingOverlay />
                }
              }
              throw err
            },
            children: [
              {
                ...eventsRoute(client, eventAPI),
                Component() {
                  return (
                    <SimpleLayout>
                      <Title title="Registrations">
                        <Subtitle subtitle="View registrations">
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
      <RouterProvider
        router={router}
        fallbackElement={<ShowLoadingOverlay />}
      />
      <LoadingOverlay />
    </MantineProvider>
  )
})
