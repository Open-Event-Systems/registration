import { useState } from "react"
import { Box } from "@mantine/core"
import { Meta, StoryObj } from "@storybook/react"
import {
  ObjectFieldState,
  createState,
} from "@open-event-systems/interview-lib"
import { ObjectField } from "#src/components/fields/ObjectField.js"

export default {
  component: ObjectField,
} as Meta<typeof ObjectField>

const schema = {
  type: "object",
  properties: {
    field_0: {
      type: "string",
      title: "First Name",
      minLength: 1,
      maxLength: 16,
      default: "First",
      "x-type": "text",
    },
    field_1: {
      type: "string",
      title: "Last Name",
      minLength: 1,
      maxLength: 16,
      default: "Last",
      "x-type": "text",
    },
  },
  required: ["field_0", "field_1"],
}

export const Default: StoryObj<typeof ObjectField> = {
  render(args) {
    const [state] = useState(() => {
      const state = createState(schema) as ObjectFieldState
      state.value = {}
      return state
    })

    return (
      <Box sx={{ maxWidth: 300 }}>
        <ObjectField {...args} state={state} required />
      </Box>
    )
  },
}
