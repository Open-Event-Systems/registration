import { ReassignDialog } from "#src/features/queue/components/reassign-dialog/ReassignDialog"
import { Meta, StoryObj } from "@storybook/react"

const meta: Meta<typeof ReassignDialog> = {
  component: ReassignDialog,
  parameters: {
    layout: "fullscreen",
  },
}

export default meta

export const Default: StoryObj<typeof ReassignDialog> = {
  args: {
    options: ["1", "2", "3"],
    opened: true,
  },
}
