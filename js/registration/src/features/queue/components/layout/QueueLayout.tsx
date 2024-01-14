import { ShowLoadingOverlay } from "#src/components"
import { SignInDialog } from "#src/features/auth/components/dialog/SignInDialog"
import { useAuth } from "#src/features/auth/hooks"
import { Scope } from "#src/features/auth/types/AccountInfo"
import { useApp } from "#src/hooks/app"
import { NotFoundError } from "#src/utils/api"
import { Box, MantineProvider } from "@mantine/core"
import { observer } from "mobx-react-lite"
import { ReactNode } from "react"

export const QueueLayout = observer(
  ({ children }: { children?: ReactNode }) => {
    const auth = useAuth()
    const app = useApp()

    const canUse =
      auth.ready && !!auth.authInfo && auth.authInfo.hasScope(Scope.queue)

    if (auth.ready && !!auth.authInfo && !canUse) {
      throw new NotFoundError()
    }

    return (
      <Box className="QueueLayout-root">
        {canUse ? (
          <MantineProvider defaultColorScheme="dark">
            {children}
          </MantineProvider>
        ) : (
          <ShowLoadingOverlay />
        )}
        <SignInDialog.Manager authStore={auth} wretch={app.wretch} />
      </Box>
    )
  },
)

QueueLayout.displayName = "QueueLayout"
