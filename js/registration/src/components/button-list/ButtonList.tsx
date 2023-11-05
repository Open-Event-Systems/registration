import {
  Box,
  BoxProps,
  Button,
  ButtonProps,
  Divider,
  DividerProps,
  Text,
  TextProps,
  createPolymorphicComponent,
  useProps,
} from "@mantine/core"
import clsx from "clsx"
import { forwardRef } from "react"

export type ButtonListProps = BoxProps

export const ButtonList = createPolymorphicComponent<
  "div",
  ButtonListProps,
  {
    Button: typeof ButtonListButton
    Label: typeof ButtonListLabel
    Divider: typeof ButtonListDivider
  }
>((props: ButtonListProps) => {
  const { className, ...other } = useProps("ButtonList", {}, props)

  return (
    <Box
      component="div"
      className={clsx(className, "ButtonList-root")}
      role="menu"
      {...other}
    />
  )
})

ButtonList.displayName = "ButtonList"

export type ButtonListButtonProps = ButtonProps

const ButtonListButton = createPolymorphicComponent<
  "button",
  ButtonListButtonProps
>(
  forwardRef<HTMLButtonElement, ButtonListButtonProps>((props, ref) => {
    const { className, classNames, styles, unstyled, children, ...other } =
      useProps("ButtonListButton", {}, props)

    return (
      <Button
        ref={ref}
        component="button"
        className={clsx(className, "ButtonListButton-root")}
        classNames={{ inner: "ButtonListButton-inner" }}
        role="menuitem"
        variant="subtle"
        fullWidth
        {...other}
      >
        {children}
      </Button>
    )
  }),
)

ButtonListButton.displayName = "ButtonListButton"

export type ButtonListLabelProps = TextProps

const ButtonListLabel = createPolymorphicComponent<"div", ButtonListLabelProps>(
  (props: ButtonListLabelProps) => {
    const { className, ...other } = useProps("ButtonListLabel", {}, props)

    return (
      <Text
        component="div"
        className={clsx(className, "ButtonListLabel-root")}
        fz="sm"
        c="dimmed"
        {...other}
      />
    )
  },
)

ButtonListLabel.displayName = "ButtonListLabel"

export type ButtonListDividerProps = DividerProps

export const ButtonListDivider = (props: ButtonListDividerProps) => {
  const { className, ...other } = useProps("ButtonListDivider", {}, props)

  return (
    <Divider className={clsx(className, "ButtonListDivider-root")} {...other} />
  )
}

ButtonList.Button = ButtonListButton
ButtonList.Label = ButtonListLabel
ButtonList.Divider = ButtonListDivider
