import { useEvents } from "#src/features/event/hooks"
import { Event } from "#src/features/event/types"
import { Await, createLoader, useLoader } from "#src/features/loader"
import {
  Registration as IRegistration,
  RegistrationState,
} from "#src/features/registration"
import { RegistrationFields } from "#src/features/registration/components/registration/fields/RegistrationFields"
import { RegistrationFieldsContext } from "#src/features/registration/components/registration/registration/field-types/Base"
import {
  DateField,
  DateTimeField,
} from "#src/features/registration/components/registration/registration/field-types/DateField"
import { NoteField } from "#src/features/registration/components/registration/registration/field-types/NoteField"
import { OptionsField } from "#src/features/registration/components/registration/registration/field-types/OptionsField"
import { TextField } from "#src/features/registration/components/registration/registration/field-types/TextField"
import { Button, Group } from "@mantine/core"
import { IconCheck, IconX } from "@tabler/icons-react"
import { observable, toJS } from "mobx"
import { ReactNode, useState } from "react"

export type RegistrationProps = {
  registration: IRegistration
  events?: Map<string, Event>
  editable?: boolean
  onSave?: (registration: IRegistration) => void
  onCancel?: () => void
}

export const Registration = (props: RegistrationProps) => {
  const {
    registration,
    events: eventsMap,
    editable = false,
    onSave,
    onCancel,
  } = props
  const events = useEvents()

  // hacky way to clone an object
  const [editState, setEditState] = useState(() =>
    observable(JSON.parse(JSON.stringify(registration))),
  )

  const event = eventsMap
    ? eventsMap.get(registration.event_id)
    : events.getEvent(registration.event_id)
  return (
    <>
      {editable && (
        <Group>
          <Button
            leftSection={<IconCheck />}
            variant="primary"
            onClick={() => {
              const reg = toJS(editState)
              onSave && onSave(reg)
            }}
          >
            Save
          </Button>
          <Button
            leftSection={<IconX />}
            variant="outline"
            color="red"
            onClick={() => {
              onCancel && onCancel()
              setEditState(observable(registration))
            }}
          >
            Cancel
          </Button>
        </Group>
      )}
      <RegistrationFieldsContext.Provider value={[editState, event]}>
        <RegistrationFields fields={getFields(editState, editable, event)} />
      </RegistrationFieldsContext.Provider>
    </>
  )
}

const getFields = (r: IRegistration, editable: boolean, event?: Event) => {
  const fields: unknown[] = [
    ["No.", r.number],
    ["Event", event?.name || r.event_id],
    ["Created At", <DateTimeField name="date_created" />],
    r.date_updated && ["Updated At", <DateTimeField name="date_updated" />],
    ["Status", formatState(r.state)],
    (r.preferred_name || editable) && [
      "Preferred Name",
      <TextField name="preferred_name" editable={editable} />,
    ],
    (r.first_name || editable) && [
      "First Name",
      <TextField name="first_name" editable={editable} />,
    ],
    (r.last_name || editable) && [
      "Last Name",
      <TextField name="last_name" editable={editable} />,
    ],
    (r.birth_date || editable) && [
      "Birth Date",
      <DateField name="birth_date" editable={editable} />,
    ],
    (r.email || editable) && [
      "Email",
      <TextField name="email" editable={editable} />,
    ],
    ["Options", <OptionsField name="option_ids" editable={editable} />],
    (r.note || editable) && [
      "Note",
      <NoteField name="note" editable={editable} />,
    ],
  ]

  return fields.filter((v): v is [string, ReactNode] => !!v)
}

const formatState = (r: string) => {
  switch (r) {
    case RegistrationState.pending:
      return "Pending"
    case RegistrationState.created:
      return "Created"
    case RegistrationState.canceled:
      return "Canceled"
    default:
      return r
  }
}
