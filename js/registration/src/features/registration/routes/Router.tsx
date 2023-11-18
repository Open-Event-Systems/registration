import { LoadingOverlay, SimpleLayout } from "#src/components"
import { SignInDialog } from "#src/features/auth/components/dialog/SignInDialog"
import { useAuth } from "#src/features/auth/hooks"
import { EventStoreProvider } from "#src/features/event/providers"
import { RegistrationAPIProvider } from "#src/features/registration"
import { SearchPage } from "#src/features/registration/routes/SearchPage"
import { AppRoute } from "#src/routes/AppRoute"
import { NotFoundPage } from "#src/routes/NotFoundPage"
import { Outlet, createBrowserRouter } from "react-router-dom"

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
                  index: true,
                  element: <SearchPage />,
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
