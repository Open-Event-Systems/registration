import { ButtonField } from "#src/components/fields/button/ButtonField"
import { Box } from "@mantine/core"
import { FieldState, createState } from "@open-event-systems/interview-lib"
import { Meta, StoryObj } from "@storybook/react"
import { useState } from "react"

const meta: Meta<typeof ButtonField> = {
  component: ButtonField,
  decorators: [
    (Story) => (
      <Box maw={300}>
        <Story />
      </Box>
    ),
  ],
}

export default meta

export const Default: StoryObj<typeof ButtonField> = {
  render(args) {
    const [[state]] = useState(() =>
      createState({
        "x-type": "button",
        oneOf: [
          {
            const: "1",
            title: "Continue",
            "x-primary": true,
          },
          {
            const: "2",
            title: "Cancel",
          },
        ],
        default: "1",
      }),
    )

    return (
      <ButtonField state={state as FieldState<string>} onClick={args.onClick} />
    )
  },
}
