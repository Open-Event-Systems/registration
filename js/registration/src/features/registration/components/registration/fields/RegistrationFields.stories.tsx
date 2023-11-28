import { RegistrationFields } from "#src/features/registration/components/registration/fields/RegistrationFields"
import { Meta, StoryObj } from "@storybook/react"

import "./RegistrationFields.scss"
import { OptionsField } from "#src/features/registration/components/registration/options/OptionsField"
import { Note } from "#src/features/registration/components/registration/note/Note"

const meta: Meta<typeof RegistrationFields> = {
  component: RegistrationFields,
}

export default meta

export const Default: StoryObj<typeof RegistrationFields> = {
  args: {
    fields: [
      ["Status", "Created"],
      ["First Name", "Example"],
      ["Last Name", "Person"],
      [
        "Options",
        <OptionsField
          key="options"
          options={[
            { id: "standard", label: "Standard" },
            { id: "vip", label: "VIP" },
          ]}
        />,
      ],
      [
        "Note",
        <Note key="note" value={"### Example Note\n\nAn example note."} />,
      ],
    ],
  },
}
