import { Header } from "#src/components/layout/header/Header"
import {
  TitleArea,
  TitleAreaProps,
} from "#src/components/layout/title-area/TitleArea"
import { AppShell, AppShellProps, Box, useProps } from "@mantine/core"
import clsx from "clsx"
import { ReactNode } from "react"

export type AppShellLayoutProps = {
  children?: ReactNode
  TitleAreaProps?: TitleAreaProps
} & AppShellProps

export const AppShellLayout = (props: AppShellLayoutProps) => {
  const { className, children, TitleAreaProps, header, ...other } = useProps(
    "AppShellLayout",
    {},
    props,
  )

  return (
    <AppShell
      className={clsx("AppShellLayout-root", className)}
      header={{
        height: {
          base: 48,
        },
        ...header,
      }}
      {...other}
    >
      <Header />
      <AppShell.Main className="AppShellLayout-main">
        <TitleArea {...TitleAreaProps} />
        <Box className="AppShellLayout-content">{children}</Box>
      </AppShell.Main>
    </AppShell>
  )
}
