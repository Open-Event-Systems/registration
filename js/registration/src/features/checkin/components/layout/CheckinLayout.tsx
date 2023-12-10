import { SignInDialog } from "#src/features/auth/components/dialog/SignInDialog"
import { useApp } from "#src/hooks/app"
import { Box, BoxProps } from "@mantine/core"
import { ComponentPropsWithoutRef, ReactNode } from "react"

export const CheckinLayout = ({ children }: { children?: ReactNode }) => {
  const app = useApp()
  return (
    <Box className="CheckinLayout-root">
      <CheckinLayout.Header>Header</CheckinLayout.Header>
      {children}
      <SignInDialog.Manager authStore={app.authStore} wretch={app.wretch} />
    </Box>
  )
}

const CheckinLayoutHeader = (
  props: BoxProps & ComponentPropsWithoutRef<"div">,
) => {
  return <Box className="CheckinLayout-header" {...props} />
}

CheckinLayout.Header = CheckinLayoutHeader

const CheckinLayoutLeft = (
  props: BoxProps & ComponentPropsWithoutRef<"div">,
) => {
  return <Box className="CheckinLayout-left" {...props} />
}

CheckinLayout.Left = CheckinLayoutLeft

const CheckinLayoutRight = (
  props: BoxProps & ComponentPropsWithoutRef<"div">,
) => {
  return <Box className="CheckinLayout-right" {...props} />
}

CheckinLayout.Right = CheckinLayoutRight

const CheckinLayoutBody = (
  props: BoxProps & ComponentPropsWithoutRef<"div">,
) => {
  return <Box className="CheckinLayout-body" {...props} />
}

CheckinLayout.Body = CheckinLayoutBody
