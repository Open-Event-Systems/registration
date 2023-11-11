import { Exit } from "#src/components/steps/exit/Exit"
import { Meta, StoryObj } from "@storybook/react"

import "./Exit.module.css"
import { Box } from "@mantine/core"

const meta: Meta<typeof Exit> = {
  component: Exit,
}

export default meta

export const Default: StoryObj<typeof Exit> = {
  decorators: [
    (Story) => (
      <Box maw={300}>
        <Story />
      </Box>
    ),
  ],
  args: {
    content: `
### Exit

Example **exit** view.
    `,
  },
}
