import { Search } from "#src/features/checkin/components/search/Search"
import {
  Registration,
  RegistrationSearchResult,
} from "#src/features/registration"
import { Meta, StoryObj } from "@storybook/react"

import "./Search.css"

const meta: Meta<typeof Search> = {
  component: Search,
}

export default meta

export const Default: StoryObj<typeof Search> = {
  args: {
    registrations: [
      {
        first_name: "Example",
        last_name: "Person",
        email: "test1@example.net",
      } as RegistrationSearchResult,
      {
        first_name: "Example",
        preferred_name: "John",
        last_name: "Person",
        email: "test1@example.net",
      } as RegistrationSearchResult,
      {
        first_name: "Example",
        last_name: "Person",
        email: "test1@example.net",
      } as RegistrationSearchResult,
    ],
  },
}

export const No_Results: StoryObj<typeof Search> = {
  args: {
    registrations: [],
  },
}

export const Next_In_line: StoryObj<typeof Search> = {
  args: {
    registrations: [],
    nextInLine: [
      {
        id: "1",
        registration: {
          id: "1",
          first_name: "Next",
          last_name: "Person",
        } as Registration,
      },
      {
        id: "2",
      },
    ],
  },
}
