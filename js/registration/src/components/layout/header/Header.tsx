import { UserMenu } from "#src/components/layout/user-menu/UserMenu"
import { useAuth } from "#src/features/auth/hooks"
import { Scope } from "#src/features/auth/types/AccountInfo"
import {
  ActionIcon,
  ActionIconProps,
  AppShell,
  AppShellHeaderProps,
  Box,
  useProps,
} from "@mantine/core"
import { IconHome } from "@tabler/icons-react"
import clsx from "clsx"
import { observer } from "mobx-react-lite"
import { ComponentType } from "react"

export type HeaderProps = {
  homeUrl?: string
  homeIcon?: ComponentType<Record<string, never>> | string
  HomeIconProps?: ActionIconProps
} & AppShellHeaderProps

export const Header = observer((props: HeaderProps) => {
  const {
    className,
    homeUrl,
    homeIcon: HomeIcon,
    HomeIconProps,
    children,
    ...other
  } = useProps("Header", {}, props)

  const authStore = useAuth()

  let userMenu

  if (
    authStore.accessToken &&
    (!authStore.scope || !authStore.scope.includes(Scope.kiosk))
  ) {
    userMenu = (
      <UserMenu
        username={authStore.email || "Guest"}
        onSignOut={() => {
          authStore.signOut()
        }}
      />
    )
  }

  let homeIcon

  if (!authStore.scope || !authStore.scope.includes(Scope.kiosk)) {
    homeIcon = (
      <ActionIcon
        className="Header-homeIcon"
        variant="transparent"
        component="a"
        href={homeUrl ?? "/"}
        title="Home"
        {...HomeIconProps}
      >
        {typeof HomeIcon === "function" ? (
          <HomeIcon />
        ) : typeof HomeIcon === "string" ? (
          <img src={HomeIcon} alt="" />
        ) : (
          <IconHome />
        )}
      </ActionIcon>
    )
  }

  return (
    <AppShell.Header className={clsx("Header-root", className)} {...other}>
      {homeIcon}
      <Box className="Header-content">{children}</Box>
      {userMenu}
    </AppShell.Header>
  )
})

Header.displayName = "Header"
