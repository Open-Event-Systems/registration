import { RegistrationState } from "#src/features/registration"
import { Registration } from "#src/features/registration/components/registration/Registration"
import { Box } from "@mantine/core"
import { Meta, StoryObj } from "@storybook/react"

import "./Registration.module.css"

const meta: Meta<typeof Registration> = {
  component: Registration,
  decorators: [
    (Story) => (
      <Box maw={500}>
        <Story />
      </Box>
    ),
  ],
}

export default meta

export const Default: StoryObj<typeof Registration> = {
  args: {
    registration: {
      id: "1234",
      event_id: "example-event",
      date_created: "2020-01-01T00:00:00-05:00",
      state: RegistrationState.created,
      email: "test@example.net",
      option_ids: ["standard", "vip"],
      version: 1,
      preferred_name: "John",
      first_name: "Example",
      last_name: "Person",
      number: 101,
    },
  },
}
