import { SimpleLayout, Subtitle, Title } from "#src/components"
import { SignInDialog } from "#src/features/auth/components/dialog/SignInDialog"
import { useAuth } from "#src/features/auth/hooks"
import { Scope } from "#src/features/auth/types/AccountInfo"
import { useApp } from "#src/hooks/app"
import { NotFoundError } from "#src/utils/api"
import { observer } from "mobx-react-lite"
import { ReactNode } from "react"

export const CheckoutLayout = observer(
  ({ children }: { children?: ReactNode }) => {
    const app = useApp()
    const auth = useAuth()

    const canUse =
      auth.ready &&
      !!auth.authInfo &&
      auth.authInfo.hasScope(Scope.event) &&
      auth.authInfo.hasScope(Scope.checkout)

    if (auth.ready && !!auth.authInfo && !canUse) {
      throw new NotFoundError()
    }

    return (
      <SimpleLayout>
        <Title title="Checkouts">
          <Subtitle subtitle="Search checkouts">
            {children}
            <SignInDialog.Manager authStore={auth} wretch={app.wretch} />
          </Subtitle>
        </Title>
      </SimpleLayout>
    )
  },
)

CheckoutLayout.displayName = "CheckoutLayout"
