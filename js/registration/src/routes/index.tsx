import {
  LoadingOverlay,
  ShowLoadingOverlay,
  SimpleLayout,
} from "#src/components"
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
        // Self service
        {
          async lazy() {
            await Promise.all([
              import("#src/features/auth/styles.css"),
              import("#src/features/interview/styles.css"),
              import("#src/features/cart/styles.css"),
            ])
            const { SelfServiceLayout } = await import(
              "#src/features/selfservice/routes/SelfServiceLayout"
            )
            return {
              element: <LayoutRoute Layout={SelfServiceLayout} />,
            }
          },
          children: [
            {
              errorElement: <NotFoundErrorBoundary />,
              children: [
                {
                  path: "/events/:eventId",
                  async lazy() {
                    const { EventRoute } = await import(
                      "#src/features/selfservice/routes/EventRoute"
                    )
                    return {
                      element: <EventRoute />,
                    }
                  },
                  children: [
                    {
                      index: true,
                      async lazy() {
                        const { EventPage } = await import(
                          "#src/features/selfservice/routes/EventPage"
                        )
                        return {
                          element: <EventPage />,
                        }
                      },
                    },
                    {
                      path: "cart",
                      async lazy() {
                        const { CartPage } = await import(
                          "#src/features/selfservice/routes/CartPage"
                        )
                        return {
                          element: <CartPage />,
                        }
                      },
                    },
                    {
                      path: "access-code/:accessCode",
                      async lazy() {
                        const { AccessCodeRoute } = await import(
                          "#src/features/selfservice/routes/AccessCodeRoute"
                        )
                        return {
                          element: <AccessCodeRoute />,
                        }
                      },
                      children: [
                        {
                          index: true,
                          async lazy() {
                            const { EventRoute } = await import(
                              "#src/features/selfservice/routes/EventRoute"
                            )
                            return {
                              element: <EventRoute />,
                            }
                          },
                        },
                      ],
                    },
                  ],
                },
              ],
            },
          ],
        },

        // Registration
        {
          path: "/registrations",
          async lazy() {
            await Promise.all([
              import("#src/features/auth/styles.css"),
              import(
                "#src/features/registration/components/registration/fields/RegistrationFields.scss"
              ),
              import(
                "#src/features/registration/components/registration/registration/Registration.module.scss"
              ),
              import(
                "#src/features/registration/components/search/Results.scss"
              ),
            ])
            const { RegistrationLayout } = await import(
              "#src/features/registration/routes/RegistrationLayout"
            )
            return {
              element: <LayoutRoute Layout={RegistrationLayout} />,
            }
          },
          children: [
            {
              errorElement: <NotFoundErrorBoundary />,
              children: [
                {
                  index: true,
                  async lazy() {
                    const { SearchPage } = await import(
                      "#src/features/registration/routes/SearchPage"
                    )

                    return {
                      element: <SearchPage />,
                    }
                  },
                },
                {
                  path: ":registrationId",
                  async lazy() {
                    const { RegistrationPage } = await import(
                      "#src/features/registration/routes/RegistrationPage"
                    )

                    return {
                      element: <RegistrationPage />,
                    }
                  },
                },
              ],
            },
          ],
        },
        {
          element: <LayoutRoute Layout={SimpleLayout} />,
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
        <RouterProvider
          router={router}
          fallbackElement={<ShowLoadingOverlay />}
        />
        <LoadingOverlay />
      </MantineProvider>
    </QueryClientProvider>
  )
})