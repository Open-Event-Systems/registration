import {
  SignInOption,
  SignInOptions,
} from "#src/features/auth/types/SignInOptions"
import {
  Box,
  BoxProps,
  NavLink,
  NavLinkProps,
  createPolymorphicComponent,
  useProps,
} from "@mantine/core"
import clsx from "clsx"
import { ComponentPropsWithoutRef } from "react"

/**
 * Sign in options menu.
 */
export type SignInOptionsProps = {
  onSelect?: (id: keyof SignInOptions) => void
  options: SignInOption[]
  OptionProps?: Partial<OptionProps & ComponentPropsWithoutRef<"button">>
} & BoxProps

export const SignInOptionsMenu = (props: SignInOptionsProps) => {
  const { className, options, onSelect, OptionProps, ...other } = useProps(
    "SignInOptionsMenu",
    {},
    props,
  )

  const children = options.map((opt) => (
    <Option
      key={opt.id}
      {...OptionProps}
      option={opt}
      onClick={onSelect ? () => onSelect(opt.id) : undefined}
    />
  ))

  return (
    <Box className={clsx("SignInOptionsMenu-root", className)} {...other}>
      {children}
    </Box>
  )
}

type OptionProps = NavLinkProps & {
  option: SignInOption
  onClick?: () => void
}

const Option = createPolymorphicComponent<"button", OptionProps>(
  (props: OptionProps) => {
    const { option, onClick, ...other } = props

    const Icon = option.icon

    return (
      <NavLink
        component="button"
        className="SignInOptionsMenuOption-root"
        label={option.name}
        description={option.description}
        leftSection={Icon ? <Icon /> : undefined}
        active={option.highlight}
        onClick={(e) => {
          e.preventDefault()
          onClick && onClick()
        }}
        {...other}
      />
    )
  },
)

Option.displayName = "Option"

type SignInOptionsOptionProps = NavLinkProps & {
  onClick?: () => void
}

export const SignInOptionsOption = createPolymorphicComponent<
  "button",
  SignInOptionsOptionProps
>((props: SignInOptionsOptionProps) => {
  const { onClick, ...other } = props

  return (
    <NavLink
      component="button"
      className="SignInOptionsMenuOption-root"
      onClick={(e) => {
        e.preventDefault()
        onClick && onClick()
      }}
      {...other}
    />
  )
})

SignInOptionsOption.displayName = "SignInOptionsOption"
