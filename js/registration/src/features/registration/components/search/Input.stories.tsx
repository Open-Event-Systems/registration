import { Input } from "#src/features/registration/components/search/Input"
import { Meta, StoryObj } from "@storybook/react"

const meta: Meta<typeof Input> = {
  component: Input,
  parameters: {
    layout: "centered",
  },
}

export default meta

export const Default: StoryObj<typeof Input> = {}
