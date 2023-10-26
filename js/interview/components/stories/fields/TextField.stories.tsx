import { TextField } from "#src/components/fields/TextField.js"
import { useState } from "react"
import { Box } from "@mantine/core"
import { Meta, StoryObj } from "@storybook/react"
import { createFormState } from "@open-event-systems/interview-lib"

export default {
  component: TextField,
} as Meta<typeof TextField>

const schema = {
  type: "string",
  "x-type": "text",
  title: "Text Input",
  description: "Example text input",
  minLength: 2,
  maxLength: 16,
  pattern: "^[abcd]+$",
}

const optionalSchema = {
  type: ["string", "null"],
  "x-type": "text",
  title: "Text Input",
  description: "Example text input",
  minLength: 2,
  maxLength: 16,
  pattern: "^[abcd]+$",
}

const emailSchema = {
  type: "string",
  "x-type": "text",
  title: "Email",
  description: "Example text input",
  format: "email",
}

export const Default: StoryObj<typeof TextField> = {
  args: {
    required: true,
  },
  render(args) {
    const [state] = useState(() => createFormState(schema))

    return (
      <Box sx={{ maxWidth: 300 }}>
        <TextField {...args} state={state} path={[]} />
      </Box>
    )
  },
}

export const Optional: StoryObj<typeof TextField> = {
  args: {
    required: false,
  },
  render(args) {
    const [state] = useState(() => createFormState(optionalSchema))

    return (
      <Box sx={{ maxWidth: 300 }}>
        <TextField {...args} state={state} path={[]} />
      </Box>
    )
  },
}
export const Email: StoryObj<typeof TextField> = {
  args: {
    required: true,
  },
  render(args) {
    const [state] = useState(() => createFormState(emailSchema))

    return (
      <Box sx={{ maxWidth: 300 }}>
        <TextField {...args} state={state} path={[]} />
      </Box>
    )
  },
}
