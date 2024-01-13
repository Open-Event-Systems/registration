import "@mantine/core/styles.css"
import "@open-event-systems/interview-components/styles.css"
import "#src/components/styles.css"
import "#src/features/auth/styles.css"
import theme from "#src/config/theme"

import "#src/config/theme.scss"

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
import { Outlet, RouterProvider, createBrowserRouter } from "react-router-dom"

import { FullScreenLayout } from "#src/components/layout/FullScreenLayout"
import { useAuth } from "#src/features/auth/hooks"
import { useApp } from "#src/hooks/app"
import { SignInDialog } from "#src/features/auth/components/dialog/SignInDialog"

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
      element: <AppRoute queryClient={client} />,
      children: [
        // Auth routes
        {
          Component() {
            const auth = useAuth()
            const app = useApp()
            return (
              <FullScreenLayout>
                <Outlet />
                <SignInDialog.Manager authStore={auth} wretch={app.wretch} />
              </FullScreenLayout>
            )
          },
          children: [
            {
              path: "/auth/authorize-device",
              async lazy() {
                const [{ DeviceAuthPage }] = await Promise.all([
                  import("#src/features/auth/routes/DeviceAuthPage"),
                ])

                return {
                  element: <DeviceAuthPage />,
                }
              },
            },
          ],
        },

        // Self service
        {
          async lazy() {
            await Promise.all([
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
                            const { EventPage } = await import(
                              "#src/features/selfservice/routes/EventPage"
                            )
                            return {
                              element: <EventPage />,
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
          ErrorBoundary() {
            return (
              <SimpleLayout>
                <NotFoundErrorBoundary />
              </SimpleLayout>
            )
          },
          path: "/registrations",
          async lazy() {
            await Promise.all([
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

        // Admin checkout management
        {
          ErrorBoundary() {
            return (
              <SimpleLayout>
                <NotFoundErrorBoundary />
              </SimpleLayout>
            )
          },
          path: "/checkouts",
          async lazy() {
            await Promise.all([
              import("#src/features/checkout/styles.scss"),
              import("#src/features/cart/styles.css"),
            ])
            const { CheckoutLayout } = await import(
              "#src/features/checkout/components/layout/CheckoutLayout"
            )
            return {
              element: <LayoutRoute Layout={CheckoutLayout} />,
            }
          },
          children: [
            {
              index: true,
              async lazy() {
                const { CheckoutSearchPage } = await import(
                  "#src/features/checkout/routes/search/CheckoutSearchPage"
                )
                return {
                  element: <CheckoutSearchPage />,
                }
              },
            },
            {
              path: "/checkouts/cart/:cartId",
              async lazy() {
                const { CheckoutCartPage } = await import(
                  "#src/features/checkout/routes/search/CheckoutCartPage"
                )
                return {
                  element: <CheckoutCartPage />,
                }
              },
            },
          ],
        },

        // check-in
        {
          ErrorBoundary() {
            return (
              <SimpleLayout>
                <NotFoundErrorBoundary />
              </SimpleLayout>
            )
          },
          children: [
            {
              async lazy() {
                const res = await Promise.all([
                  await import(
                    "#src/features/checkin/components/layout/CheckinLayout"
                  ),
                  await import("#src/features/interview/styles.css"),
                  await import(
                    "#src/features/checkin/components/layout/CheckinLayout.scss"
                  ), // TODO: import styles.css instead
                  await import(
                    "#src/features/checkin/components/search/Search.css"
                  ), // TODO: import styles.css instead
                  await import(
                    "#src/features/checkin/components/badge/Badge.css"
                  ), // TODO: import styles.css instead
                  await import("#src/features/checkin/routes/CheckinPage.css"), // TODO: import styles.css instead
                  await import(
                    "#src/features/registration/components/registration/fields/RegistrationFields.scss"
                  ), // TODO: import styles.css instead
                ])
                const [{ CheckinLayout }] = res
                return {
                  element: <LayoutRoute Layout={CheckinLayout} />,
                }
              },
              children: [
                {
                  path: "/check-in/:eventId",
                  async lazy() {
                    const { SearchPage } = await import(
                      "#src/features/checkin/routes/SearchPage"
                    )
                    return {
                      element: <SearchPage />,
                    }
                  },
                },
                {
                  path: "/check-in/:eventId/registrations/:registrationId",
                  async lazy() {
                    const { CheckinPage } = await import(
                      "#src/features/checkin/routes/CheckinPage"
                    )
                    return {
                      element: <CheckinPage />,
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
