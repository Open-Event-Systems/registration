import { InterviewOptionsDialog } from "#src/features/cart/components/interview/InterviewOptionsDialog"
import { Meta, StoryObj } from "@storybook/react"

export default {
  component: InterviewOptionsDialog,
  parameters: {
    layout: "fullscreen",
  },
} as Meta<typeof InterviewOptionsDialog>

export const Default: StoryObj<typeof InterviewOptionsDialog> = {
  args: {
    opened: true,
    options: [
      { id: "opt1", name: "Option 1" },
      { id: "opt2", name: "Option 2" },
      { id: "opt3", name: "Option 3 (Slow)" },
      { id: "opt4", name: "Option 4" },
    ],
    onSelect: (opt) => {
      if (opt.id == "opt3") {
        const wait = new Promise<void>((r) => window.setTimeout(r, 1000))
        return wait
      }
    },
  },
}
