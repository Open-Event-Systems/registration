import { SignInDialog } from "#src/features/auth/components/dialog/SignInDialog"
import { useApp } from "#src/hooks/app"
import { Box, BoxProps } from "@mantine/core"
import clsx from "clsx"
import {
  ComponentPropsWithRef,
  ComponentPropsWithoutRef,
  ReactNode,
  createContext,
  useCallback,
  useState,
} from "react"

export const CheckinLayout = ({ children }: { children?: ReactNode }) => {
  const app = useApp()
  return (
    <Box className="CheckinLayout-root">
      {children}
      <SignInDialog.Manager authStore={app.authStore} wretch={app.wretch} />
    </Box>
  )
}

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
