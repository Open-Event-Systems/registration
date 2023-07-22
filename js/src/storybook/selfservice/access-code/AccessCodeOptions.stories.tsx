import { AccessCodeOptions } from "#src/features/selfservice/components/access-code/AccessCodeOptions.js"
import { Meta, StoryObj } from "@storybook/react"

export default {
  component: AccessCodeOptions,
} as Meta<typeof AccessCodeOptions>

export const Add: StoryObj<typeof AccessCodeOptions> = {
  args: {
    registrations: [],
    interviews: [
      { id: "opt-1", name: "Option 1" },
      { id: "opt-2", name: "Option 2" },
    ],
  },
}

export const Change: StoryObj<typeof AccessCodeOptions> = {
  args: {
    registrations: [
      { id: "reg-a", title: "Person A" },
      { id: "reg-b", title: "Person B" },
    ],
    interviews: [
      { id: "opt-1", name: "Option 1" },
      { id: "opt-2", name: "Option 2" },
    ],
  },
}

export const Both: StoryObj<typeof AccessCodeOptions> = {
  args: {
    registrations: [
      { id: "reg-a", title: "Person A" },
      { id: "reg-b", title: "Person B" },
    ],
    interviews: [
      { id: "opt-1", name: "Option 1" },
      { id: "opt-2", name: "Option 2" },
    ],
  },
}
