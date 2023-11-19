import { RegistrationState } from "#src/features/registration"
import { Registration } from "#src/features/registration/components/registration/registration/Registration"
import { Meta, StoryObj } from "@storybook/react"

import "@mantine/dates/styles.css"
import "../fields/RegistrationFields.scss"

const meta: Meta<typeof Registration> = {
  component: Registration,
}

export default meta

export const Default: StoryObj<typeof Registration> = {
  args: {
    editable: false,
    events: new Map([
      [
        "example-event",
        {
          id: "1",
          name: "Example Event",
          date: "2020-01-01",
          open: true,
          visible: true,
          registration_options: [
            { id: "standard", name: "Standard" },
            { id: "vip", name: "VIP" },
          ],
        },
      ],
    ]),
    registration: {
      id: "1",
      event_id: "example-event",
      state: RegistrationState.created,
      date_created: "2020-01-01T12:00:00-05:00",
      date_updated: "2020-10-01T17:00:00-04:00",
      option_ids: ["standard"],
      version: 1,
      email: "test@example.com",
      first_name: "Example",
      last_name: "Person",
      preferred_name: "John",
      birth_date: "2000-01-01",
      number: 101,
    },
  },
}
