import {
  DefaultProps,
  NavLink,
  NavLinkProps,
  NavLinkStylesNames,
  Selectors,
  Stack,
  StackProps,
  createStyles,
  useComponentDefaultProps,
} from "@mantine/core"
import { ComponentPropsWithoutRef, ElementType } from "react"

const useStyles = createStyles({
  root: {},
})

export type DialogMenuProps = Omit<StackProps, "styles"> &
  DefaultProps<Selectors<typeof useStyles>>

export const DialogMenu = (props: DialogMenuProps) => {
  const { className, classNames, styles, unstyled, children, ...other } =
    useComponentDefaultProps("DialogMenu", {}, props)

  const { classes, cx } = useStyles(undefined, {
    name: "DialogMenu",
    classNames,
    styles,
    unstyled,
  })

  return (
    <Stack className={cx(classes.root, className)} spacing={0} {...other}>
      {children}
    </Stack>
  )
}

const useItemStyles = createStyles((theme) => ({
  root: {
    padding: `${theme.spacing.sm} ${theme.spacing.md}`,
    "&:hover": {
      color: theme.white,
    },
  },
}))

export type DialogMenuItemProps = NavLinkProps &
  DefaultProps<NavLinkStylesNames | Selectors<typeof useItemStyles>>

export const DialogMenuItem = <C extends ElementType = "button">(
  props: DialogMenuItemProps & { component?: C } & ComponentPropsWithoutRef<C>
) => {
  const { className, classNames, styles, unstyled, ...other } =
    useComponentDefaultProps("DialogMenuItem", {}, props)

  const { classes, cx } = useItemStyles(undefined, {
    name: "DialogMenuItem",
    classNames,
    styles,
    unstyled,
  })

  return (
    <NavLink
      className={cx(classes.root, className)}
      active
      variant="subtle"
      {...other}
    />
  )
}
