import { AccessCodeOptionsDialog } from "#src/features/selfservice/components/access-code/AccessCodeOptionsDialog.js"
import { Meta, StoryObj } from "@storybook/react"

export default {
  component: AccessCodeOptionsDialog,
} as Meta<typeof AccessCodeOptionsDialog>

export const Default: StoryObj<typeof AccessCodeOptionsDialog> = {
  args: {
    opened: true,
    response: {
      add_options: [{ id: "new-registration", name: "New Registration" }],
      registrations: [
        {
          registration: {
            id: "reg-1",
            title: "Person A",
          },
          change_options: [
            { id: "change-name", name: "Change Name" },
            { id: "upgrade", name: "Upgrade" },
          ],
        },
        {
          registration: {
            id: "reg-2",
            title: "Person B",
          },
          change_options: [{ id: "change-name", name: "Change Name" }],
        },
      ],
    },
  },
}
