import { RegistrationState } from "#src/features/registration"
import { Search } from "#src/features/registration/components/search/Search"
import { Meta, StoryObj } from "@storybook/react"

const meta: Meta<typeof Search> = {
  component: Search,
}

export default meta

export const Default: StoryObj<typeof Search> = {
  args: {
    events: [
      { id: "event-1", name: "Event 1" },
      { id: "event-2", name: "Event 2" },
    ],
    registrations: [
      {
        id: "1",
        event_id: "1",
        state: RegistrationState.created,
        first_name: "John",
        last_name: "Example",
        email: "john@example.net",
        number: 101,
      },
      {
        id: "2",
        event_id: "1",
        state: RegistrationState.created,
        first_name: "John",
        last_name: "Example",
        email: "john@example.net",
        number: 102,
      },
      {
        id: "3",
        event_id: "1",
        state: RegistrationState.created,
        preferred_name: "John",
        first_name: "Johnathan",
        last_name: "Example",
        email: "john@example.net",
        number: 103,
      },
      {
        id: "4",
        event_id: "1",
        state: RegistrationState.created,
        first_name: "John",
        last_name: "Example",
        email: "john@example.net",
        number: 104,
      },
      {
        id: "5",
        event_id: "1",
        state: RegistrationState.created,
        first_name: "John",
        last_name: "Example",
        email: "john@example.net",
        number: 105,
      },
    ],
    getLink(r) {
      return [`#${r.id}`, r.id]
    },
    InputProps: {
      SelectProps: {
        defaultValue: "event-1",
      },
    },
  },
}
