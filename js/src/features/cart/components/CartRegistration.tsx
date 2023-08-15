import {
  ActionIcon,
  DefaultProps,
  Selectors,
  Title,
  createStyles,
  useComponentDefaultProps,
} from "@mantine/core"
import { IconTrash } from "@tabler/icons-react"
import { ReactNode } from "react"

const useStyles = createStyles((theme) => ({
  name: {
    [`@media (max-width: ${theme.breakpoints.xs})`]: {},
    gridColumn: "item-name-start / item-name-end",
    justifySelf: "start",
    alignSelf: "center",
    marginTop: theme.spacing.sm,
  },
  removeIcon: {
    [`@media (max-width: ${theme.breakpoints.xs})`]: {},
    gridColumn: "icon-start / icon-end",
    justifySelf: "start",
    alignSelf: "center",
    marginTop: theme.spacing.sm,
  },
}))

export type CartRegistrationProps = {
  name?: string
  children?: ReactNode
  onRemove?: () => void
} & Omit<DefaultProps<Selectors<typeof useStyles>>, "className">

export const CartRegistration = (props: CartRegistrationProps) => {
  const { classNames, styles, unstyled, name, onRemove, children } =
    useComponentDefaultProps("CartRegistration", {}, props)

  const { classes } = useStyles(void 0, {
    name: "CartRegistration",
    classNames,
    styles,
    unstyled,
  })

  const removeIcon = onRemove ? (
    <ActionIcon
      key="remove"
      title={`Remove ${name || "Registration"}`}
      className={classes.removeIcon}
      onClick={() => {
        onRemove && onRemove()
      }}
    >
      <IconTrash />
    </ActionIcon>
  ) : (
    <div key="spacer" role="separator"></div>
  )

  return [
    removeIcon,
    <Title key="name" className={classes.name} order={4}>
      {name || "Registration"}
    </Title>,
    children,
  ]
}
