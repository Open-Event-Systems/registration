import {
  ActionIcon,
  Card,
  CardProps,
  Grid,
  Menu,
  Skeleton,
  SkeletonProps,
  Text,
  Title,
  useProps,
} from "@mantine/core"
import { IconDotsVertical } from "@tabler/icons-react"
import clsx from "clsx"
import { ReactNode } from "react"

export type RegistrationCardProps = {
  title?: ReactNode
  subtitle?: ReactNode
  menuOptions?: { id: string; label: string }[]
  onMenuSelect?: (id: string) => void
  children?: ReactNode
} & CardProps

export const RegistrationCard = (props: RegistrationCardProps) => {
  const {
    className,
    title,
    subtitle,
    menuOptions,
    onMenuSelect,
    children,
    ...other
  } = useProps("RegistrationCard", { menuOptions: [] }, props)

  return (
    <Card
      className={clsx("RegistrationCard-root", className)}
      padding="xs"
      shadow="xs"
      {...other}
    >
      <Grid justify="flex-end" align="flex-start">
        <Grid.Col span="auto" style={{ minWidth: 0 }}>
          <Title order={3} className="RegistrationCard-title">
            {title}
          </Title>
          <Text className="RegistrationCard-subtitle" c="gray">
            {subtitle}
          </Text>
        </Grid.Col>
        {menuOptions.length > 0 && (
          <Grid.Col span="content">
            <Menu withinPortal>
              <Menu.Target>
                <ActionIcon
                  title="Show registration options"
                  color="gray"
                  variant="subtle"
                >
                  <IconDotsVertical />
                </ActionIcon>
              </Menu.Target>
              <Menu.Dropdown>
                <Menu.Label>Options</Menu.Label>
                {menuOptions.map((opt) => (
                  <Menu.Item
                    key={opt.id}
                    onClick={() => onMenuSelect && onMenuSelect(opt.id)}
                  >
                    {opt.label}
                  </Menu.Item>
                ))}
              </Menu.Dropdown>
            </Menu>
          </Grid.Col>
        )}
      </Grid>
      {children}
    </Card>
  )
}

export type RegistrationCardPlaceholderProps = SkeletonProps

export const RegistrationCardPlaceholder = (
  props: RegistrationCardPlaceholderProps,
) => {
  const { className, height, ...other } = useProps(
    "RegistrationCardPlaceholder",
    { height: 150 },
    props,
  )

  return (
    <Skeleton
      className={clsx("RegistrationCardPlaceholder-root", className)}
      height={height}
      {...other}
    />
  )
}
