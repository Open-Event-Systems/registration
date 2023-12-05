import { DeviceAuthRequest } from "#src/features/auth/components/device/auth/DeviceAuthRequest"
import { Meta, StoryObj } from "@storybook/react"

import "./DeviceAuthRequest.css"

const meta: Meta<typeof DeviceAuthRequest> = {
  component: DeviceAuthRequest,
  parameters: {
    layout: "centered",
  },
}

export default meta

export const Default: StoryObj<typeof DeviceAuthRequest> = {
  args: {
    url: "http://localhost:6006/#",
    userCode: "123456",
  },
}
