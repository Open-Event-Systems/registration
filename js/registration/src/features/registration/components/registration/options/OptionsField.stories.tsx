import { OptionsField } from "#src/features/registration/components/registration/options/OptionsField"
import { Box } from "@mantine/core"
import { Meta, StoryObj } from "@storybook/react"

const meta: Meta<typeof OptionsField> = {
  component: OptionsField,
  parameters: {
    layout: "centered",
  },
  decorators: [
    (Story) => (
      <Box maw={300}>
        <Story />
      </Box>
    ),
  ],
}

export default meta

export const Default: StoryObj<typeof OptionsField> = {
  args: {
    options: [
      { id: "standard", label: "Standard" },
      { id: "deluxe", label: "Deluxe" },
      { id: "premium", label: "Premium" },
      { id: "vip", label: "VIP" },
    ],
    readOnly: false,
  },
}
