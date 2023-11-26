import { RegistrationState } from "#src/features/registration"
import { Results } from "#src/features/registration/components/search/Results"
import { Meta, StoryObj } from "@storybook/react"

import "./Results.scss"
import { useState } from "react"
import { RegistrationSearchResult } from "#src/features/registration"

const meta: Meta<typeof Results> = {
  component: Results,
  parameters: {
    layout: "centered",
  },
}

export default meta

export const Default: StoryObj<typeof Results> = {
  args: {
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
  },
  render(args) {
    const { registrations, onMore, ...other } = args
    const [more, setMore] = useState<RegistrationSearchResult[] | undefined>(
      undefined,
    )
    const [allowMore, setAllowMore] = useState(true)

    const handleMore = async () => {
      await new Promise((r) => window.setTimeout(r, 1000))
      if (more) {
        setAllowMore(false)
      } else {
        setMore([
          {
            id: "6",
            event_id: "1",
            state: RegistrationState.created,
            first_name: "John",
            last_name: "Example",
            email: "john@example.net",
            number: 106,
          },
          {
            id: "7",
            event_id: "1",
            state: RegistrationState.created,
            first_name: "John",
            last_name: "Example",
            email: "john@example.net",
            number: 107,
          },
          {
            id: "8",
            event_id: "1",
            state: RegistrationState.created,
            first_name: "John",
            last_name: "Example",
            email: "john@example.net",
            number: 108,
          },
        ])
      }
    }

    return (
      <Results
        registrations={[...(registrations ?? []), ...(more ?? [])]}
        hasMore={allowMore}
        onMore={handleMore}
        {...other}
      />
    )
  },
}
