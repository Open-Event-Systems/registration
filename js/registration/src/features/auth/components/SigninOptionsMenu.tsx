import {
  SignInOption,
  SignInOptions,
} from "#src/features/auth/types/SignInOptions.js"
import {
  Box,
  BoxProps,
  DefaultProps,
  NavLink,
  NavLinkProps,
  Selectors,
  createStyles,
  useComponentDefaultProps,
} from "@mantine/core"
import { ComponentPropsWithRef } from "react"

const useStyles = createStyles({
  root: {},
  option: {},
})

/**
 * Sign in options menu.
 */
export type SigninOptionsProps = {
  onSelect?: (id: keyof SignInOptions) => void
  options: SignInOption[]
  OptionProps?: Partial<OptionProps>
} & Omit<BoxProps, "children" | "styles"> &
  DefaultProps<Selectors<typeof useStyles>>

export const SigninOptionsMenu = (props: SigninOptionsProps) => {
  const {
    className,
    classNames,
    styles,
    unstyled,
    options,
    onSelect,
    OptionProps,
    ...other
  } = useComponentDefaultProps("SigninOptionsMenu", {}, props)

  const { classes, cx } = useStyles(undefined, {
    name: "SigninOptionsMenu",
    classNames,
    styles,
    unstyled,
  })

  const children = options.map((opt) => (
    <Option
      key={opt.id}
      {...OptionProps}
      option={opt}
      onClick={onSelect ? () => onSelect(opt.id) : undefined}
    />
  ))

  return (
    <Box className={cx(classes.root, className)} {...other}>
      {children}
    </Box>
  )
}

type OptionProps = NavLinkProps &
  ComponentPropsWithRef<"button"> & {
    option: SignInOption
    onClick?: () => void
  }

const Option = (props: OptionProps) => {
  const { option, onClick, ...other } = props

  const Icon = option.icon

  return (
    <NavLink
      label={option.name}
      description={option.description}
      icon={Icon ? <Icon /> : undefined}
      active={option.highlight}
      sx={{
        "&:focus": {
          outline: "none",
        },
      }}
      onClick={(e) => {
        e.preventDefault()
        onClick && onClick()
      }}
      {...other}
    />
  )
}
