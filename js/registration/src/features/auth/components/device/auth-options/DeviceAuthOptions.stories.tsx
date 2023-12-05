import {
  DeviceAuthOptions,
  DeviceAuthOptionsProps,
} from "#src/features/auth/components/device/auth-options/DeviceAuthOptions"
import { Scope } from "#src/features/auth/types/AccountInfo"
import { Meta, StoryObj } from "@storybook/react"
import { useState } from "react"

import "./DeviceAuthOptions.css"

const meta: Meta<typeof DeviceAuthOptions> = {
  component: DeviceAuthOptions,
  parameters: {
    layout: "centered",
  },
}

export default meta

export const Default: StoryObj<typeof DeviceAuthOptions> = {
  render(args) {
    const [value, setValue] = useState<DeviceAuthOptionsProps["value"]>({
      account: "my_account",
      email: "",
      requireWebAuthn: false,
      scope: [Scope.cart, Scope.selfService],
    })

    return <DeviceAuthOptions {...args} value={value} onChange={setValue} />
  },
}
