import {
  Group,
  SimpleGrid,
  SimpleGridProps,
  Text,
  TextProps,
  useProps,
} from "@mantine/core"
import { IconAlertCircle } from "@tabler/icons-react"
import clsx from "clsx"

export type CardGridProps = SimpleGridProps

export const CardGrid = (props: CardGridProps) => {
  const { className, children, ...other } = useProps("CardGrid", {}, props)

  return (
    <SimpleGrid
      className={clsx("CardGrid-root", className)}
      spacing="sm"
      cols={{
        base: 1,
        xs: 2,
        md: 3,
      }}
      {...other}
    >
      {children}
    </SimpleGrid>
  )
}

export const NoRegistrationsMessage = (props: TextProps) => (
  <Text c="dimmed" component="div" {...props}>
    <Group align="center">
      <IconAlertCircle />
      <Text span inline>
        You have no registrations for this event.
      </Text>
    </Group>
  </Text>
)
