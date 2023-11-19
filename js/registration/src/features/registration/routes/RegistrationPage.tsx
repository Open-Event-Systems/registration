import { Subtitle, Title } from "#src/components"
import { useEvents } from "#src/features/event/hooks"
import { Event } from "#src/features/event/types"
import { createLoader } from "#src/features/loader"
import { Registration, RegistrationState } from "#src/features/registration"
import { RegistrationFields } from "#src/features/registration/components/registration/fields/RegistrationFields"
import { OptionsField } from "#src/features/registration/components/registration/options/OptionsField"
import { useRegistration } from "#src/features/registration/hooks"
import { RegistrationStore } from "#src/features/registration/stores/registration"
import { Text } from "@mantine/core"
import dayjs from "dayjs"
import { action } from "mobx"
import { ReactNode } from "react"

export const RegistrationPage = () => {
  const events = useEvents()
  const regLoader = useRegistration()
  const registration = createLoader(() =>
    regLoader.then((reg) => new RegistrationStore(reg)),
  )

  return (
    <registration.Component
      notFound={
        <Title title="Not Found">
          <Text component="p">The registration was not found.</Text>
        </Title>
      }
      placeholder={<>Loading</>}
    >
      {(reg) => {
        const fields = getFields(
          reg.registration,
          events.loader.value ?? new Map(),
        ).filter((f): f is [string, ReactNode] => !!f)

        return (
          <Title title={formatName(reg.registration)}>
            <Subtitle subtitle="View registration">
              <RegistrationFields fields={fields} />
            </Subtitle>
          </Title>
        )
      }}
    </registration.Component>
  )
}

const formatName = (r: Registration) => {
  const names = [r.preferred_name || r.first_name, r.last_name]
    .filter((v) => !!v)
    .join(" ")
  return names || r.email || "Registration"
}

const getFields = (
  r: Registration,
  events: Map<string, Event>,
): ([string, ReactNode] | null | false | "" | undefined)[] => [
  ["No.", r.number],
  ["Event", events.get(r.event_id)?.name || r.event_id],
  ["Created At", formatDate(r.date_created)],
  r.date_updated && ["Updated At", formatDate(r.date_updated)],
  ["Status", formatState(r.state)],
  r.preferred_name && ["Preferred Name", r.preferred_name],
  r.first_name && ["First Name", r.first_name],
  r.last_name && ["Last Name", r.last_name],
  r.email && ["Email", r.email],
  [
    "Options",
    <OptionsField
      options={r.option_ids.map((o) => ({ id: o }))}
      selectedOptions={r.option_ids}
      onChange={action((v) => (r.option_ids = v))}
    />,
  ],
]

const formatState = (r: string) => {
  switch (r) {
    case RegistrationState.pending:
      return "Pending"
    case RegistrationState.created:
      return "Created"
    case RegistrationState.canceled:
      return "Canceled"
    default:
      r
  }
}

const formatDate = (d: string) => {
  const date = dayjs(d)
  if (date.isValid()) {
    return date.format("YYYY-MM-DD HH:mm Z")
  } else {
    return d
  }
}
