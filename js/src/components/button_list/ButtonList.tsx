import {
  Box,
  BoxProps,
  Button,
  ButtonProps,
  DefaultProps,
  Divider,
  DividerProps,
  DividerStylesNames,
  Selectors,
  Text,
  TextProps,
  createPolymorphicComponent,
  createStyles,
  useComponentDefaultProps,
} from "@mantine/core"
import { ForwardedRef, forwardRef } from "react"

const useButtonListStyles = createStyles({
  root: {},
})

export type ButtonListProps = BoxProps &
  DefaultProps<Selectors<typeof useButtonListStyles>>

const _ButtonList = forwardRef(
  (props: ButtonListProps, ref: ForwardedRef<HTMLDivElement>) => {
    const { className, classNames, styles, unstyled, children, ...other } =
      useComponentDefaultProps("ButtonList", {}, props)

    const { classes, cx } = useButtonListStyles(void 0, {
      name: "ButtonList",
      classNames,
      styles,
      unstyled,
    })
    return (
      <Box
        ref={ref}
        component="div"
        className={cx(classes.root, className)}
        role="menu"
        {...other}
      >
        {children}
      </Box>
    )
  }
)

_ButtonList.displayName = "ButtonList"

export const ButtonList = createPolymorphicComponent<
  "div",
  ButtonListProps,
  {
    Button: typeof ButtonListButton
    Label: typeof ButtonListLabel
    Divider: typeof ButtonListDivider
  }
>(_ButtonList)

const useButtonListButtonStyles = createStyles((theme) => ({
  root: {
    display: "block",
    padding: `0 ${theme.spacing.xs}`,
  },
  inner: {
    justifyContent: "flex-start",
  },
}))

export type ButtonListButtonProps = ButtonProps &
  DefaultProps<Selectors<typeof useButtonListButtonStyles>>

const _ButtonListButton = forwardRef<HTMLButtonElement, ButtonListButtonProps>(
  (props, ref) => {
    const { className, classNames, styles, unstyled, children, ...other } =
      useComponentDefaultProps("ButtonListButton", {}, props)

    const { classes, cx } = useButtonListButtonStyles(void 0, {
      name: "ButtonListButton",
      classNames,
      styles,
      unstyled,
    })

    return (
      <Button
        ref={ref}
        component="button"
        className={cx(classes.root, className)}
        classNames={{ inner: classes.inner }}
        role="menuitem"
        variant="subtle"
        fullWidth
        {...other}
      >
        {children}
      </Button>
    )
  }
)

_ButtonListButton.displayName = "ButtonListButton"

export const ButtonListButton = createPolymorphicComponent<
  "button",
  ButtonListButtonProps
>(_ButtonListButton)

const useButtonListLabelStyles = createStyles((theme) => ({
  root: {
    display: "block",
    padding: `0.25rem ${theme.spacing.xs}`,
    cursor: "default",
  },
}))

export type ButtonListLabelProps = TextProps &
  DefaultProps<Selectors<typeof useButtonListLabelStyles>>

const _ButtonListLabel = (props: ButtonListLabelProps) => {
  const { className, classNames, styles, unstyled, children, ...other } =
    useComponentDefaultProps("ButtonListLabel", {}, props)

  const { classes, cx } = useButtonListLabelStyles(void 0, {
    name: "ButtonListLabel",
    classNames,
    styles,
    unstyled,
  })
  return (
    <Text
      component="div"
      className={cx(classes.root, className)}
      fz="sm"
      c="dimmed"
      {...other}
    >
      {children}
    </Text>
  )
}

export const ButtonListLabel = createPolymorphicComponent<
  "div",
  ButtonListLabelProps
>(_ButtonListLabel)

const useButtonListDividerStyles = createStyles({
  root: {
    margin: "0.25rem 0",
  },
})

export type ButtonListDividerProps = DividerProps &
  DefaultProps<
    Selectors<typeof useButtonListDividerStyles> | DividerStylesNames
  >

export const ButtonListDivider = (props: ButtonListDividerProps) => {
  const { className, classNames, styles, unstyled, ...other } =
    useComponentDefaultProps("ButtonListDivider", {}, props)

  const { classes, cx } = useButtonListDividerStyles(void 0, {
    name: "ButtonListDivider",
    classNames,
    styles,
    unstyled,
  })
  return <Divider className={cx(classes.root, className)} {...other} />
}

ButtonList.Button = ButtonListButton
ButtonList.Label = ButtonListLabel
ButtonList.Divider = ButtonListDivider
