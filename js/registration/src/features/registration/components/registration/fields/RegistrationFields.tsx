import { Box, BoxProps, useProps } from "@mantine/core"
import clsx from "clsx"
import { ComponentPropsWithoutRef, ReactNode } from "react"

export type RegistrationFieldsProps = Omit<
  RegistrationFieldsRootProps,
  "children"
> & {
  fields?: [string, ReactNode][]
}

export const RegistrationFields = (props: RegistrationFieldsProps) => {
  const { fields = [], ...other } = useProps("RegistrationFields", {}, props)

  const fieldNodes: ReactNode[] = []

  fields.forEach(([name, value]) =>
    fieldNodes.push(
      <RegistrationFields.Name key={`${name}-name`}>
        {name}
      </RegistrationFields.Name>,
      <RegistrationFields.Value key={`${name}-value`}>
        {value}
      </RegistrationFields.Value>,
    ),
  )

  return (
    <RegistrationFields.Root {...other}>{fieldNodes}</RegistrationFields.Root>
  )
}

export type RegistrationFieldsRootProps = BoxProps &
  ComponentPropsWithoutRef<"div">

const RegistrationFieldsRoot = (props: RegistrationFieldsRootProps) => {
  const { className, ...other } = useProps("RegistrationFieldsRoot", {}, props)

  return (
    <Box className={clsx("RegistrationFields-root", className)} {...other} />
  )
}

export type RegistrationFieldsNameProps = BoxProps &
  ComponentPropsWithoutRef<"div">

const RegistrationFieldsName = (props: RegistrationFieldsNameProps) => {
  const { className, ...other } = useProps("RegistrationFieldsName", {}, props)

  return (
    <Box className={clsx("RegistrationFields-name", className)} {...other} />
  )
}

export type RegistrationFieldsValueProps = BoxProps &
  ComponentPropsWithoutRef<"div">

const RegistrationFieldsValue = (props: RegistrationFieldsValueProps) => {
  const { className, ...other } = useProps("RegistrationFieldsValue", {}, props)

  return (
    <Box className={clsx("RegistrationFields-value", className)} {...other} />
  )
}

RegistrationFields.Root = RegistrationFieldsRoot
RegistrationFields.Name = RegistrationFieldsName
RegistrationFields.Value = RegistrationFieldsValue
