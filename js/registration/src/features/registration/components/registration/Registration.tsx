import {
  Registration as IRegistration,
  RegistrationState,
} from "#src/features/registration"
import { Box, BoxProps, Title, TitleProps, useProps } from "@mantine/core"
import clsx from "clsx"
import { ComponentPropsWithoutRef, ReactNode } from "react"

type FieldFormatter = (registration: IRegistration) => string | null | undefined

export type RegistrationProps = {
  registration: IRegistration
  fields?: Record<string, string | FieldFormatter>
} & Omit<RegistrationRootProps, "children">

const formatState = (r: IRegistration): string => {
  switch (r.state) {
    case RegistrationState.created:
      return "Created"
    case RegistrationState.pending:
      return "Pending"
    case RegistrationState.canceled:
      return "Canceled"
    default:
      return r.state
  }
}

const formatOptions = (r: IRegistration): string => {
  return r.option_ids.join(", ")
}

const defaultFields: Record<string, string | FieldFormatter> = {
  Status: formatState,
  "Date Created": "date_created",
  "Preferred Name": "preferred_name",
  "First Name": "first_name",
  "Last Name": "last_name",
  Email: "email",
  Number: "number",
  "Option IDs": formatOptions,
}

export const Registration = (props: RegistrationProps) => {
  const { registration, fields, ...other } = useProps("Registration", {}, props)

  const withDefaults = {
    ...defaultFields,
    ...fields,
  }

  const rowNodes = Object.entries(withDefaults)
    .map(([name, formatter]) => {
      let value
      if (typeof formatter === "string") {
        value = registration[formatter]
      } else {
        value = formatter(registration)
      }

      if (value == null) {
        return null
      }

      return <Registration.Row name={name} value={String(value)} />
    })
    .filter((v) => v != null)

  return (
    <Registration.Root {...other}>
      <Registration.Name>{formatName(registration)}</Registration.Name>
      {rowNodes}
    </Registration.Root>
  )
}

const formatName = (registration: IRegistration): string => {
  const name = [
    registration.preferred_name || registration.first_name,
    registration.last_name,
  ]
    .filter((v) => !!v)
    .join(" ")

  return name || registration.email || "Registration"
}

export type RegistrationRootProps = BoxProps & ComponentPropsWithoutRef<"div">

const RegistrationRoot = (props: RegistrationRootProps) => {
  const { className, ...other } = useProps("RegistrationRoot", {}, props)

  return <Box className={clsx("Registration-root", className)} {...other} />
}

export type RegistrationNameProps = TitleProps

const RegistrationName = (props: RegistrationNameProps) => {
  const { className, ...other } = useProps(
    "RegistrationName",
    {
      order: 3,
    },
    props,
  )

  return <Title className={clsx("Registration-name", className)} {...other} />
}

export type RegistrationRowProps = {
  name?: ReactNode
  value?: ReactNode
  className?: string
}

const RegistrationRow = (props: RegistrationRowProps) => {
  const { name, value, className } = useProps("RegistrationRow", {}, props)

  return [
    <Box key="name" className={clsx("Registration-rowName", className)}>
      {name}
    </Box>,
    <Box key="value" className={clsx("Registration-rowValue", className)}>
      {value}
    </Box>,
  ]
}

Registration.Root = RegistrationRoot
Registration.Name = RegistrationName
Registration.Row = RegistrationRow
