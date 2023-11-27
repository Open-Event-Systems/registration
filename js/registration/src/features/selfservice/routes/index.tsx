import {
  LoadingOverlay,
  ShowLoadingOverlay,
  SimpleLayout,
  Subtitle,
  Title,
} from "#src/components"
import { isNotFoundError } from "#src/util/api"
import { makeApp } from "#src/util/react"
import { MantineProvider } from "@mantine/core"
import {
  QueryClient,
  QueryClientProvider,
  useQuery,
} from "@tanstack/react-query"
import {
  Outlet,
  RouterProvider,
  createBrowserRouter,
  useParams,
} from "react-router-dom"

import { AppRoute } from "#src/routes/AppRoute"
import { ReactNode } from "react"

import { useApp } from "#src/hooks/app"
import { useAuth } from "#src/features/auth/hooks"
import { useSelfServiceAPI } from "#src/features/selfservice/hooks"
import { SignInDialog } from "#src/features/auth/components/dialog/SignInDialog"

import "@mantine/core/styles.css"
import "@open-event-systems/interview-components/styles.css"
import "#src/components/styles.css"
import "#src/features/auth/styles.css"
import "#src/features/interview/styles.css"
import "#src/features/cart/styles.css"
import theme from "#src/config/theme"
import { LayoutRoute } from "#src/routes/LayoutRoute"
import { EventPage } from "#src/features/selfservice/routes/EventPage"
import { CurrentCartStoreProvider } from "#src/features/cart/providers"
import { CartPage } from "#src/features/selfservice/routes/CartPage"

const SelfServiceLayout = ({ children }: { children?: ReactNode }) => {
  const app = useApp()
  const auth = useAuth()
  const selfService = useSelfServiceAPI()
  const query = useQuery(selfService.listEvents())

  return (
    <SimpleLayout>
      <Title title="Registrations">
        <Subtitle subtitle="Manage registrations">
          {query.isSuccess ? children : <ShowLoadingOverlay />}
          <SignInDialog.Manager authStore={auth} wretch={app.wretch} />
        </Subtitle>
      </Title>
    </SimpleLayout>
  )
}

makeApp(() => {
  const client = new QueryClient({
    defaultOptions: {
      queries: {
        retry(failureCount, error) {
          if (isNotFoundError(error)) {
            return false
          } else {
            return failureCount < 3
          }
        },
        throwOnError(error) {
          if (isNotFoundError(error)) {
            return true
          } else {
            return false
          }
        },
      },
    },
  })

  const router = createBrowserRouter([
    {
      element: (
        <AppRoute queryClient={client} fallback={<ShowLoadingOverlay />} />
      ),
      children: [
        {
          element: <LayoutRoute Layout={SelfServiceLayout} />,
          children: [
            {
              path: "/events/:eventId",
              Component() {
                const { eventId = "" } = useParams()
                return (
                  <CurrentCartStoreProvider key={eventId} eventId={eventId}>
                    <Outlet />
                  </CurrentCartStoreProvider>
                )
              },
              children: [
                {
                  index: true,
                  element: <EventPage />,
                },
                {
                  path: "cart",
                  element: <CartPage />,
                },
              ],
            },
          ],
        },
      ],
    },
  ])

  return (
    <QueryClientProvider client={client}>
      <MantineProvider theme={theme}>
        <RouterProvider router={router} />
        <LoadingOverlay />
      </MantineProvider>
    </QueryClientProvider>
  )
})
