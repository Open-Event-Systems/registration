import { Input } from "#src/features/registration/components/search/Input"
import { Meta, StoryObj } from "@storybook/react"

const meta: Meta<typeof Input> = {
  component: Input,
  parameters: {
    layout: "centered",
  },
}

export default meta

export const Default: StoryObj<typeof Input> = {
  args: {
    SelectProps: {
      data: [
        { value: "e1", label: "Event 1" },
        { value: "e2", label: "Event 2" },
        { value: "e3", label: "Event 3" },
      ],
      defaultValue: "e1",
    },
  },
}
