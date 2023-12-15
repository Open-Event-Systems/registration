import {
  ShowLoadingOverlay,
  SimpleLayout,
  Subtitle,
  Title,
} from "#src/components"
import { ConfirmationDialog } from "#src/components/confirm/ConfirmDialog"
import { SignInDialog } from "#src/features/auth/components/dialog/SignInDialog"
import { useAuth } from "#src/features/auth/hooks"
import { useEventAPI } from "#src/features/event/hooks"
import { useApp } from "#src/hooks/app"
import { useQuery } from "@tanstack/react-query"
import { ReactNode } from "react"

export const RegistrationLayout = ({ children }: { children?: ReactNode }) => {
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
      <ConfirmationDialog />
    </SimpleLayout>
  )
}
