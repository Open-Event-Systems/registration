import { useState } from "react"
import { Box } from "@mantine/core"
import { NumberField } from "#src/components/fields/NumberField.js"
import { Meta, StoryObj } from "@storybook/react"
import { createState } from "@open-event-systems/interview-lib"

export default {
  component: NumberField,
} as Meta<typeof NumberField>

const schema = {
  type: "integer",
  "x-type": "number",
  title: "Number Input",
  description: "Example number input",
  minimum: 1,
  maximum: 10,
  nullable: true,
}

export const Default: StoryObj<typeof NumberField> = {
  render(args) {
    const [state] = useState(() => createState(schema))

    return (
      <Box sx={{ maxWidth: 300 }}>
        <NumberField {...args} state={state} required={false} />
      </Box>
    )
  },
}
