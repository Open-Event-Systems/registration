import { ButtonList } from "#src/components/button-list/ButtonList.js"
import { Box } from "@mantine/core"
import { Meta, StoryObj } from "@storybook/react"
import { IconUserPlus, IconZoomExclamation } from "@tabler/icons-react"

import "./ButtonList.module.css"

const meta: Meta<typeof ButtonList> = {
  component: ButtonList,
}

export default meta

export const Default: StoryObj<typeof ButtonList> = {
  decorators: [
    (Story) => (
      <Box maw={300}>
        <Story />
      </Box>
    ),
  ],
  render: (args) => (
    <ButtonList {...args}>
      <ButtonList.Label>Stuff</ButtonList.Label>
      <ButtonList.Button leftSection={<IconUserPlus />}>
        Option 1
      </ButtonList.Button>
      <ButtonList.Button>Option 2</ButtonList.Button>
      <ButtonList.Divider />
      <ButtonList.Label>More Stuff</ButtonList.Label>
      <ButtonList.Button leftSection={<IconZoomExclamation />}>
        Option 3
      </ButtonList.Button>
    </ButtonList>
  ),
}