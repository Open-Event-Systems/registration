import { ShowLoadingOverlay } from "#src/components"
import { AppProvider } from "#src/providers/AppProvider"
import { ReactNode } from "react"
import { Outlet, isRouteErrorResponse, useRouteError } from "react-router-dom"

export const AppRoute = ({ fallback }: { fallback?: ReactNode }) => (
  <AppProvider fallback={fallback}>
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
