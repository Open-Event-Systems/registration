import {
  RegistrationCard,
  RegistrationCardPlaceholder,
} from "#src/features/selfservice/components/card/RegistrationCard.js"
import { Meta, StoryObj } from "@storybook/react"

import "./RegistrationCard.module.css"

const meta: Meta<typeof RegistrationCard> = {
  component: RegistrationCard,
  args: {
    title: "Person 1",
    subtitle: "Standard",
    maw: 300,
  },
}

export default meta

export const Default: StoryObj<typeof RegistrationCard> = {
  render(args) {
    return (
      <RegistrationCard
        menuOptions={[
          { id: "1", label: "Upgrade" },
          { id: "2", label: "Rename" },
          { id: "3", label: "Cancel" },
        ]}
        {...args}
      >
        Content
      </RegistrationCard>
    )
  },
}

export const Placeholder: StoryObj<typeof RegistrationCardPlaceholder> = {
  render() {
    return <RegistrationCardPlaceholder maw={300} />
  },
}
