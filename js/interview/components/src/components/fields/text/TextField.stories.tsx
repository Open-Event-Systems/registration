import { TextField } from "#src/components/fields/text/TextField.js"
import { Box } from "@mantine/core"
import { FieldState, createState } from "@open-event-systems/interview-lib"
import { Meta, StoryObj } from "@storybook/react"
import { useState } from "react"

const meta: Meta<typeof TextField> = {
  component: TextField,
  decorators: [
    (Story) => (
      <Box maw={300}>
        <Story />
      </Box>
    ),
  ],
}

export default meta

export const Default: StoryObj<typeof TextField> = {
  render() {
    const [state] = useState(() =>
      createState({
        type: "string",
        title: "Name",
        minLength: 2,
        maxLength: 16,
      }),
    )

    return <TextField required state={state as FieldState<string>} />
  },
}
