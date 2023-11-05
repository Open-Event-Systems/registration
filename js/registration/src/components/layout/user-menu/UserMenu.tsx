import { Anchor, AnchorProps, Menu, MenuProps, useProps } from "@mantine/core"
import { IconLogout } from "@tabler/icons-react"

export type UserMenuProps = {
  username?: string | null
  onSignOut?: () => void
  AnchorProps?: Partial<AnchorProps>
} & Omit<MenuProps, "children">

export const UserMenu = (props: UserMenuProps) => {
  const { username, onSignOut, AnchorProps, ...other } = useProps(
    "UserMenu",
    {},
    props,
  )

  return (
    <Menu shadow="sm" {...other}>
      <Menu.Target>
        <Anchor
          className="UserMenu-anchor"
          component="button"
          aria-label="User options"
          {...AnchorProps}
        >
          {username}
        </Anchor>
      </Menu.Target>
      <Menu.Dropdown>
        <Menu.Label>Options</Menu.Label>
        <Menu.Item leftSection={<IconLogout />} onClick={onSignOut}>
          Sign Out
        </Menu.Item>
      </Menu.Dropdown>
    </Menu>
  )
}
