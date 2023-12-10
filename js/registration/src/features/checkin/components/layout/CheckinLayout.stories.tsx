import { CheckinLayout } from "#src/features/checkin/components/layout/CheckinLayout"
import { Meta, StoryObj } from "@storybook/react"

import "#src/components/styles.css"
import "./CheckinLayout.css"

const meta: Meta<typeof CheckinLayout> = {
  component: CheckinLayout,
  parameters: {
    layout: "fullscreen",
  },
}

export default meta

export const Two_Panel: StoryObj<typeof CheckinLayout> = {
  render(args) {
    return (
      <CheckinLayout {...args}>
        <CheckinLayout.Left>Left</CheckinLayout.Left>
        <CheckinLayout.Right>Right</CheckinLayout.Right>
      </CheckinLayout>
    )
  },
}

export const One_Panel: StoryObj<typeof CheckinLayout> = {
  render(args) {
    return (
      <CheckinLayout {...args}>
        <CheckinLayout.Body>Body</CheckinLayout.Body>
      </CheckinLayout>
    )
  },
}
