import { ActionIcon, Title, useProps } from "@mantine/core"
import { IconTrash } from "@tabler/icons-react"
import clsx from "clsx"
import { ReactNode } from "react"

export type CartRegistrationProps = {
  name?: string
  children?: ReactNode
  onRemove?: () => void
  classNames?: {
    name?: string
    removeIcon?: string
  }
}

export const CartRegistration = (props: CartRegistrationProps) => {
  const { classNames, name, onRemove, children } = useProps(
    "CartRegistration",
    {},
    props,
  )

  const removeIcon = onRemove ? (
    <ActionIcon
      key="remove"
      title={`Remove ${name || "Registration"}`}
      className={clsx("CartRegistration-removeIcon", classNames?.removeIcon)}
      onClick={() => {
        onRemove && onRemove()
      }}
      variant="transparent"
      c="dimmed"
    >
      <IconTrash />
    </ActionIcon>
  ) : (
    <div key="spacer" role="separator"></div>
  )

  return [
    removeIcon,
    <Title
      key="name"
      className={clsx("CartRegistration-name", classNames?.name)}
      order={4}
    >
      {name || "Registration"}
    </Title>,
    children,
  ]
}
