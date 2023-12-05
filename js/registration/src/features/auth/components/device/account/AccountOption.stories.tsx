import {
  AccountOption,
  AccountOptionProps,
} from "#src/features/auth/components/device/account/AccountOption"
import { Meta, StoryObj } from "@storybook/react"
import { useState } from "react"

const meta: Meta<typeof AccountOption> = {
  component: AccountOption,
  parameters: {
    layout: "centered",
  },
}

export default meta

export const Default: StoryObj<typeof AccountOption> = {
  render(args) {
    const [state, setState] = useState<AccountOptionProps["value"]>({
      account: "my_account",
      email: "",
    })
    return <AccountOption {...args} value={state} onChange={setState} />
  },
}
