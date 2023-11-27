import {
  LoadingOverlay,
  ShowLoadingOverlay,
  SimpleLayout,
  Subtitle,
  Title,
} from "#src/components"
import { makeApp } from "#src/utils/react"
import { MantineProvider } from "@mantine/core"
import { RouterProvider, createBrowserRouter } from "react-router-dom"

import { SearchPage } from "#src/features/registration/routes/SearchPage"
import { RegistrationPage } from "#src/features/registration/routes/RegistrationPage"
import {
  QueryClient,
  QueryClientProvider,
  useQuery,
} from "@tanstack/react-query"
import { AppRoute, AuthErrorBoundary } from "#src/routes/AppRoute"
import { LayoutRoute } from "#src/routes/LayoutRoute"
import { useAuth } from "#src/features/auth/hooks"
import { useApp } from "#src/hooks/app"
import { ReactNode } from "react"
import { SignInDialog } from "#src/features/auth/components/dialog/SignInDialog"
import { useEventAPI } from "#src/features/event/hooks"
import { isNotFoundError } from "#src/utils/api"

import "@mantine/core/styles.css"
import "@open-event-systems/interview-components/styles.css"
import "#src/components/styles.css"
import "#src/features/auth/styles.css"
import "#src/features/interview/styles.css"
import "#src/features/cart/styles.css"
import "#src/features/registration/components/search/Results.scss"
import "#src/features/registration/components/registration/fields/RegistrationFields.scss"
import theme from "#src/config/theme"

const RegistrationLayout = ({ children }: { children?: ReactNode }) => {
  const app = useApp()
  const auth = useAuth()
  const eventAPI = useEventAPI()
  const query = useQuery(eventAPI.list())

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

  const router = createBrowserRouter(
    [
      {
        element: (
          <AppRoute queryClient={client} fallback={<ShowLoadingOverlay />} />
        ),
        children: [
          {
            element: <LayoutRoute Layout={RegistrationLayout} />,
            children: [
              {
                errorElement: <AuthErrorBoundary />,
                children: [
                  {
                    index: true,
                    element: <SearchPage />,
                  },
                  {
                    path: ":registrationId",
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
    <QueryClientProvider client={client}>
      <MantineProvider theme={theme}>
        <RouterProvider router={router} />
        <LoadingOverlay />
      </MantineProvider>
    </QueryClientProvider>
  )
})
