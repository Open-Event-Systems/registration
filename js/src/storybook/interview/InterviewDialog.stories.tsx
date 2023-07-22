import { InterviewDialog } from "#src/features/interview/components/InterviewDialog.js"
import { Meta, StoryObj } from "@storybook/react"

export default {
  component: InterviewDialog,
} as Meta<typeof InterviewDialog>

export const Empty: StoryObj<typeof InterviewDialog> = {
  args: {
    opened: true,
  },
  render: (args) => <InterviewDialog {...args} />,
}

export const Question: StoryObj<typeof InterviewDialog> = {
  args: {
    opened: true,
    content: {
      type: "question",
      title: "Example Question",
      description: "An example question",
      fields: {
        field0: {
          type: "text",
          label: "Text",
          min: 0,
          max: 20,
        },
      },
    },
    onSubmit: async (values, button) => {
      await new Promise((r) => window.setTimeout(r, 1000))
    },
  },
}

export const Exit: StoryObj<typeof InterviewDialog> = {
  args: {
    opened: true,
    content: {
      type: "exit",
      title: "Exit",
      description: "Exit reason.",
    },
  },
}
