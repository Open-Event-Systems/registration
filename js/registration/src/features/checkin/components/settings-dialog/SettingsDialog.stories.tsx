import { SettingsDialog } from "#src/features/checkin/components/settings-dialog/SettingsDialog"
import { Meta, StoryObj } from "@storybook/react"

const meta: Meta<typeof SettingsDialog> = {
  component: SettingsDialog,
  parameters: {
    layout: "fullscreen",
  },
}

export default meta

export const Default: StoryObj<typeof SettingsDialog> = {
  args: {
    opened: true,
    stationIds: ["2", "3"],
  },
}
