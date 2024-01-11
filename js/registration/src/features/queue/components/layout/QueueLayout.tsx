import { SignInDialog } from "#src/features/auth/components/dialog/SignInDialog"
import { useAuth } from "#src/features/auth/hooks"
import { useApp } from "#src/hooks/app"
import { Box } from "@mantine/core"
import { ReactNode } from "react"

export const QueueLayout = ({ children }: { children?: ReactNode }) => {
  const auth = useAuth()
  const app = useApp()
  return (
    <Box className="QueueLayout-root">
      {children}
      <SignInDialog.Manager authStore={auth} wretch={app.wretch} />
    </Box>
  )
}
