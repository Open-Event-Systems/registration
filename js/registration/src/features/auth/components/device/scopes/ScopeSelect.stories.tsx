import { ScopeSelect } from "#src/features/auth/components/device/scopes/ScopeSelect"
import { Meta, StoryObj } from "@storybook/react"

const meta: Meta<typeof ScopeSelect> = {
  component: ScopeSelect,
  parameters: {
    layout: "centered",
  },
}

export default meta

export const Default: StoryObj<typeof ScopeSelect> = {}
