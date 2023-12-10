import { Event } from "#src/features/event/types"
import { Registration as IRegistration } from "#src/features/registration"
import { RegistrationFields } from "#src/features/registration/components/registration/fields/RegistrationFields"
import { RegistrationFieldsContext } from "#src/features/registration/components/registration/registration/field-types/Base"
import { NoteField } from "#src/features/registration/components/registration/registration/field-types/NoteField"
import { OptionsField } from "#src/features/registration/components/registration/registration/field-types/OptionsField"
import { TextField } from "#src/features/registration/components/registration/registration/field-types/TextField"
import { ReactNode } from "react"

export type RegistrationProps = {
  registration: IRegistration
  eventsMap?: Map<string, Event>
}

export const Registration = (props: RegistrationProps) => {
  const { registration: r, eventsMap } = props

  const event = eventsMap?.get(r.event_id)

  const fields: unknown[] = [
    r.preferred_name && [
      "Preferred Name",
      <TextField key="preferred_name" name="preferred_name" />,
    ],
    ["First Name", <TextField key="first_name" name="first_name" />],
    ["Last Name", <TextField key="last_name" name="last_name" />],
    ["Email", <TextField key="email" name="email" />],
    ["Options", <OptionsField key="option_ids" name="option_ids" />],
    r.note && ["Note", <NoteField key="note" name="note" />],
  ]

  const filteredFields = fields.filter((f): f is [string, ReactNode] => !!f)

  return (
    <RegistrationFieldsContext.Provider value={[r, event]}>
      <RegistrationFields fields={filteredFields} />
    </RegistrationFieldsContext.Provider>
  )
}
