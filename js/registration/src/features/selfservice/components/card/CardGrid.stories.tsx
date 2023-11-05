import {
  CardGrid,
  NoRegistrationsMessage,
} from "#src/features/selfservice/components/card/CardGrid.js"
import { RegistrationCard } from "#src/features/selfservice/components/card/RegistrationCard.js"
import { Meta, StoryObj } from "@storybook/react"

import "./RegistrationCard.module.css"

const meta: Meta<typeof CardGrid> = {
  component: CardGrid,
}

export default meta

export const Default: StoryObj<typeof CardGrid> = {
  render() {
    const opts = [{ id: "1", label: "Option" }]
    return (
      <CardGrid>
        <RegistrationCard
          key="p1"
          title="Person 1"
          subtitle="Standard"
          menuOptions={opts}
        >
          Example 1
        </RegistrationCard>
        <RegistrationCard
          key="p2"
          title="Person 2 With Long Name"
          subtitle="VIP"
          menuOptions={opts}
        >
          Example 2<br />
          <br />
          <br />
          <br />
          <br />
          Many lines
          <br />
          <br />
        </RegistrationCard>
        <RegistrationCard
          key="p3"
          title="Person 3"
          subtitle="Standard, Option 2, Option 3, Option 4"
          menuOptions={opts}
        >
          Example 3
        </RegistrationCard>
      </CardGrid>
    )
  },
}

export const Empty: StoryObj<typeof NoRegistrationsMessage> = {
  render() {
    return <NoRegistrationsMessage />
  },
}
