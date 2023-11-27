import {
  LoadingOverlay,
  ShowLoadingOverlay,
  SimpleLayout,
} from "#src/components"
import { AccessCodeRoute } from "#src/features/selfservice/routes/AccessCodeRoute"
import { CartPage } from "#src/features/selfservice/routes/CartPage"
import { EventPage } from "#src/features/selfservice/routes/EventPage"
import { EventRoute } from "#src/features/selfservice/routes/EventRoute"
import { SelfServiceLayout } from "#src/features/selfservice/routes/SelfServiceLayout"
import { AppRoute } from "#src/routes/AppRoute"
import { LayoutRoute } from "#src/routes/LayoutRoute"
import { NotFoundErrorBoundary, NotFoundPage } from "#src/routes/NotFoundPage"
import { isNotFoundError } from "#src/utils/api"
import { makeApp } from "#src/utils/react"
import { MantineProvider } from "@mantine/core"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { RouterProvider, createBrowserRouter } from "react-router-dom"

import "@mantine/core/styles.css"
import "@open-event-systems/interview-components/styles.css"
import "#src/components/styles.css"
import "#src/features/auth/styles.css"
import "#src/features/interview/styles.css"
import "#src/features/cart/styles.css"
import theme from "#src/config/theme"

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
              errorElement: <NotFoundErrorBoundary />,
              children: [
                {
                  path: "/events/:eventId",
                  element: <EventRoute />,
                  children: [
                    {
                      index: true,
                      element: <EventPage />,
                    },
                    {
                      path: "cart",
                      element: <CartPage />,
                    },
                    {
                      path: "access-code/:accessCode",
                      element: <AccessCodeRoute />,
                      children: [
                        {
                          index: true,
                          element: <EventPage />,
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
          element: <LayoutRoute Layout={SelfServiceLayout} />,
          children: [
            {
              path: "*",
              element: <NotFoundPage />,
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
