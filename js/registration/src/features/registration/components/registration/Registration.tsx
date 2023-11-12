import {
  Registration as IRegistration,
  RegistrationState,
} from "#src/features/registration"
import {
  Box,
  BoxProps,
  Button,
  Select,
  Skeleton,
  Title,
  TitleProps,
  useProps,
} from "@mantine/core"
import { IconHandStop, IconShoppingCartCheck } from "@tabler/icons-react"
import clsx from "clsx"
import { ComponentPropsWithoutRef, ReactNode } from "react"

type FieldFormatter = (registration: IRegistration) => string | null | undefined

export type RegistrationProps = {
  registration: IRegistration
  fields?: Record<string, string | FieldFormatter>
  actions?: { id: string; label: string }[]
  onSelectAction?: (id: string) => void
  onComplete?: () => void
  onCancel?: () => void
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
  const {
    registration,
    fields,
    actions,
    onSelectAction,
    onComplete,
    onCancel,
    ...other
  } = useProps("Registration", {}, props)

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
      <Registration.Fields>{rowNodes}</Registration.Fields>
      <Registration.Actions
        actions={actions}
        onComplete={onComplete}
        onCancel={onCancel}
      />
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

export type RegistrationFieldsProps = BoxProps & ComponentPropsWithoutRef<"div">

const RegistrationFields = (props: RegistrationFieldsProps) => {
  const { className, ...other } = useProps("RegistrationFields", {}, props)

  return <Box className={clsx("Registration-fields", className)} {...other} />
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

export type RegistrationActionsProps = BoxProps &
  Omit<ComponentPropsWithoutRef<"div">, "children"> & {
    actions?: { id: string; label: string }[]
    onSelectAction?: (id: string) => void
    onComplete?: () => void
    onCancel?: () => void
  }

const RegistrationActions = (props: RegistrationActionsProps) => {
  const { className, actions, onSelectAction, onComplete, onCancel, ...other } =
    useProps("RegistrationActions", {}, props)

  return (
    <Box className={clsx("Registration-actions", className)} {...other}>
      {onComplete && (
        <Button
          leftSection={<IconShoppingCartCheck />}
          onClick={onComplete}
          variant="outline"
        >
          Complete Registration
        </Button>
      )}
      {onCancel && (
        <Button
          leftSection={<IconHandStop />}
          onClick={onCancel}
          variant="outline"
          color="red"
        >
          Cancel Registration
        </Button>
      )}
      {actions && actions.length > 0 && (
        <Select
          placeholder="Action"
          data={actions.map((a) => ({
            value: a.id,
            label: a.label,
          }))}
          value={null}
          onChange={(v) => {
            if (v != null && onSelectAction) {
              onSelectAction(v)
            }
          }}
        />
      )}
    </Box>
  )
}

const RegistrationPlaceholder = () => (
  <Registration.Root className="Registration-placeholder">
    <Registration.Name>
      <Skeleton />
    </Registration.Name>
    <Registration.Fields>
      <Registration.Row name={<Skeleton />} value={<Skeleton />} />
      <Registration.Row name={<Skeleton />} value={<Skeleton />} />
      <Registration.Row name={<Skeleton />} value={<Skeleton />} />
      <Registration.Row name={<Skeleton />} value={<Skeleton />} />
      <Registration.Row name={<Skeleton />} value={<Skeleton />} />
      <Registration.Row name={<Skeleton />} value={<Skeleton />} />
      <Registration.Row name={<Skeleton />} value={<Skeleton />} />
      <Registration.Row name={<Skeleton />} value={<Skeleton />} />
    </Registration.Fields>
  </Registration.Root>
)

Registration.Root = RegistrationRoot
Registration.Name = RegistrationName
Registration.Fields = RegistrationFields
Registration.Row = RegistrationRow
Registration.Actions = RegistrationActions
Registration.Placeholder = RegistrationPlaceholder
