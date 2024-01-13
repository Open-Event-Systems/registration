import { Search } from "#src/features/checkout/components/search/Search"
import { Meta, StoryObj } from "@storybook/react"

import "./Search.scss"
import { CheckoutState } from "#src/features/checkout/types/Checkout"

const meta: Meta<typeof Search> = {
  component: Search,
}

export default meta

export const Default: StoryObj<typeof Search> = {
  args: {
    getLink() {
      const url = new URL(window.location.href)
      url.hash = `#`
      return url.toString()
    },
  },
}

export const With_Results: StoryObj<typeof Search> = {
  args: {
    getLink() {
      const url = new URL(window.location.href)
      url.hash = `#`
      return url.toString()
    },
    results: [
      {
        id: "checkout-5",
        date: "2020-01-01T05:00:00+00:00",
        service: "Suspend",
        state: CheckoutState.canceled,
        first_name: "Example",
        last_name: "Person",
        email: "person@example.net",
      },
      {
        id: "checkout-4",
        date: "2020-01-01T04:00:00+00:00",
        service: "System",
        state: CheckoutState.complete,
        first_name: "Example",
        last_name: "Person",
        email: "person@example.net",
      },
      {
        id: "checkout-3",
        date: "2020-01-01T03:00:00+00:00",
        service: "Suspend",
        state: CheckoutState.pending,
      },
    ],
  },
}

export const No_Results: StoryObj<typeof Search> = {
  args: {
    results: [],
  },
}
