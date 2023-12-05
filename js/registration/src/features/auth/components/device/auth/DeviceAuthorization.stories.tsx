import { DeviceAuthorization } from "#src/features/auth/components/device/auth/DeviceAuthorization"
import { Scope } from "#src/features/auth/types/AccountInfo"
import { Box } from "@mantine/core"
import { Meta, StoryObj } from "@storybook/react"

import "./DeviceAuthorization.css"

const meta: Meta<typeof DeviceAuthorization> = {
  component: DeviceAuthorization,
  parameters: {
    layout: "fullscreen",
  },
}

export default meta

export const Default: StoryObj<typeof DeviceAuthorization> = {
  decorators: [
    (Story) => {
      return (
        <Box
          maw={300}
          m="auto"
          h="100vh"
          p={16}
          display="flex"
          style={{ alignItems: "stretch", justifyContent: "center" }}
        >
          <Story />
        </Box>
      )
    },
  ],
  args: {
    client: "Registration Kiosk",
    scope: [Scope.cart, Scope.selfService],
    showOptions: false,
  },
}
