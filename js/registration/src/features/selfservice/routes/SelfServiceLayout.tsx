import {
  ShowLoadingOverlay,
  SimpleLayout,
  Subtitle,
  Title,
} from "#src/components"
import { SignInDialog } from "#src/features/auth/components/dialog/SignInDialog"
import { useAuth } from "#src/features/auth/hooks"
import { useSelfServiceAPI } from "#src/features/selfservice/hooks"
import { useApp } from "#src/hooks/app"
import { useQuery } from "@tanstack/react-query"
import { ReactNode } from "react"

export const SelfServiceLayout = ({ children }: { children?: ReactNode }) => {
  const app = useApp()
  const auth = useAuth()
  const selfService = useSelfServiceAPI()
  const query = useQuery(selfService.listEvents())

  return (
    <SimpleLayout>
      <Title title="Registrations">
        <Subtitle subtitle="Manage registrations">
          {query.isSuccess ? children : <ShowLoadingOverlay />}
          <SignInDialog.Manager2 authStore={auth} wretch={app.wretch} />
        </Subtitle>
      </Title>
    </SimpleLayout>
  )
}
