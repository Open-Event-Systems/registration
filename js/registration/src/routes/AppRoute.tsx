import { ShowLoadingOverlay } from "#src/components"
import { AppProvider } from "#src/providers/AppProvider"
import { QueryClient } from "@tanstack/react-query"
import { Outlet, isRouteErrorResponse, useRouteError } from "react-router-dom"

export const AppRoute = ({ queryClient }: { queryClient: QueryClient }) => (
  <AppProvider queryClient={queryClient}>
    <Outlet />
  </AppProvider>
)

export const AuthErrorBoundary = () => {
  const error = useRouteError()

  if (isRouteErrorResponse(error) && error.status == 401) {
    return <ShowLoadingOverlay />
  }

  throw error
}
