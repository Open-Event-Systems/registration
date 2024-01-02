import { SignInDialog } from "#src/features/auth/components/dialog/SignInDialog"
import { useAuth } from "#src/features/auth/hooks"
import { Scope } from "#src/features/auth/types/AccountInfo"
import { useApp } from "#src/hooks/app"
import { NotFoundError } from "#src/utils/api"
import { Box, BoxProps } from "@mantine/core"
import clsx from "clsx"
import { observer } from "mobx-react-lite"
import {
  ComponentPropsWithRef,
  ComponentPropsWithoutRef,
  ReactNode,
  createContext,
  useCallback,
  useState,
} from "react"

const _CheckinLayout = observer(({ children }: { children?: ReactNode }) => {
  const app = useApp()
  const auth = useAuth()

  if (auth.ready && !!auth.authInfo && !auth.authInfo.hasScope(Scope.checkIn)) {
    throw new NotFoundError()
  }

  return (
    <Box className="CheckinLayout-root">
      {children}
      <SignInDialog.Manager authStore={app.authStore} wretch={app.wretch} />
    </Box>
  )
})

_CheckinLayout.displayName = "CheckinLayout"

export const CheckinLayout = (props: { children?: ReactNode }) => (
  <_CheckinLayout {...props} />
)

const CheckinLayoutHeader = (
  props: BoxProps & ComponentPropsWithRef<"div">,
) => {
  return <Box className="CheckinLayout-header" {...props} />
}

CheckinLayout.Header = CheckinLayoutHeader

const CheckinLayoutSpacer = (
  props: BoxProps & ComponentPropsWithRef<"div">,
) => {
  return <Box className="CheckinLayout-spacer" {...props} />
}

CheckinLayout.Spacer = CheckinLayoutSpacer

const CheckinLayoutLeft = (
  props: BoxProps & ComponentPropsWithoutRef<"div">,
) => {
  const { className, ...other } = props
  return <Box className={clsx("CheckinLayout-left", className)} {...other} />
}

CheckinLayout.Left = CheckinLayoutLeft

const CheckinLayoutCenter = (
  props: BoxProps & ComponentPropsWithoutRef<"div">,
) => {
  const { className, ...other } = props
  return <Box className={clsx("CheckinLayout-center", className)} {...other} />
}

CheckinLayout.Center = CheckinLayoutCenter

const CheckinLayoutRight = (
  props: BoxProps & ComponentPropsWithoutRef<"div">,
) => {
  const { className, ...other } = props
  return <Box className={clsx("CheckinLayout-right", className)} {...other} />
}

CheckinLayout.Right = CheckinLayoutRight

const CheckinLayoutBody = (
  props: BoxProps & ComponentPropsWithoutRef<"div">,
) => {
  const { className, ...other } = props
  return <Box className={clsx("CheckinLayout-body", className)} {...other} />
}

CheckinLayout.Body = CheckinLayoutBody
