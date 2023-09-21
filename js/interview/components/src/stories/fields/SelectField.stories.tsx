import { Box } from "@mantine/core"
import { SelectField } from "#src/components/fields/SelectField.js"
import { Meta, StoryObj } from "@storybook/react"
import { useState } from "react"
import { createState } from "@open-event-systems/interview-lib"

export default {
  component: SelectField,
} as Meta<typeof SelectField>

const dropdown = {
  type: "string",
  "x-type": "select",
  title: "Test",
  oneOf: [
    {
      const: "1",
      title: "Option 1",
    },
    {
      const: "2",
      title: "Option 2",
    },
    {
      const: "3",
      title: "Option 3",
    },
  ],
}

const radio = {
  type: "string",
  "x-type": "select",
  "x-component": "radio",
  title: "Test",
  oneOf: [
    {
      const: "1",
      title: "Option 1",
    },
    {
      const: "2",
      title: "Option 2",
    },
    {
      const: "3",
      title: "Option 3",
    },
  ],
}

const checkbox = {
  type: "array",
  "x-type": "select",
  "x-component": "checkbox",
  title: "Test",
  items: {
    oneOf: [
      {
        const: "1",
        title: "Option 1",
      },
      {
        const: "2",
        title: "Option 2",
      },
      {
        const: "3",
        title: "Option 3",
      },
    ],
  },
  minItems: 1,
  maxItems: 2,
}

const booleanSelect = {
  type: "string",
  "x-type": "select",
  "x-component": "checkbox",
  oneOf: [
    {
      const: "1",
      title: "I accept",
    },
    { type: "null" },
  ],
  const: "1",
  nullable: true,
}

export const Dropdown: StoryObj<typeof SelectField> = {
  render(args) {
    const [state] = useState(() => createState(dropdown))

    return (
      <Box sx={{ maxWidth: 300 }}>
        <SelectField {...args} state={state} required />
      </Box>
    )
  },
}

export const Radio: StoryObj<typeof SelectField> = {
  render(args) {
    const [state] = useState(() => createState(radio))

    return (
      <Box sx={{ maxWidth: 300 }}>
        <SelectField {...args} state={state} required />
      </Box>
    )
  },
}

export const Checkbox: StoryObj<typeof SelectField> = {
  render(args) {
    const [state] = useState(() => createState(checkbox))

    return (
      <Box sx={{ maxWidth: 300 }}>
        <SelectField {...args} state={state} required />
      </Box>
    )
  },
}

export const Boolean: StoryObj<typeof SelectField> = {
  render(args) {
    const [state] = useState(() => createState(booleanSelect))

    return (
      <Box sx={{ maxWidth: 300 }}>
        <SelectField {...args} state={state} required />
      </Box>
    )
  },
}
