import {
  ShowLoadingOverlay,
  SimpleLayout,
  Subtitle,
  Title,
} from "#src/components"
import { ConfirmationDialog } from "#src/components/confirm/ConfirmDialog"
import { SignInDialog } from "#src/features/auth/components/dialog/SignInDialog"
import { useAuth } from "#src/features/auth/hooks"
import { Scope } from "#src/features/auth/types/AccountInfo"
import { useEventAPI } from "#src/features/event/hooks"
import { useApp } from "#src/hooks/app"
import { NotFoundError } from "#src/utils/api"
import { useQuery } from "@tanstack/react-query"
import { observer } from "mobx-react-lite"
import { ReactNode } from "react"

export const RegistrationLayout = observer(
  ({ children }: { children?: ReactNode }) => {
    const app = useApp()
    const auth = useAuth()
    const eventAPI = useEventAPI()

    const canUse =
      auth.ready &&
      !!auth.authInfo &&
      auth.authInfo.hasScope(Scope.event) &&
      auth.authInfo.hasScope(Scope.registration)

    const query = useQuery({
      ...eventAPI.list(),
      enabled: canUse,
    })

    if (auth.ready && !!auth.authInfo && !canUse) {
      throw new NotFoundError()
    }

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
  },
)
