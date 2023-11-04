import { SelectField } from "#src/components/fields/select/SelectField.js"
import { Box } from "@mantine/core"
import { FieldState, createState } from "@open-event-systems/interview-lib"
import { Meta, StoryObj } from "@storybook/react"
import { useState } from "react"

import "./Checkbox.module.css"
import "./Radio.module.css"

const meta: Meta<typeof SelectField> = {
  component: SelectField,
  decorators: [
    (Story) => (
      <Box maw={300}>
        <Story />
      </Box>
    ),
  ],
}

export default meta

export const Dropdown: StoryObj<typeof SelectField> = {
  render() {
    const [[state]] = useState(() =>
      createState({
        title: "Select",
        "x-component": "dropdown",
        oneOf: [
          {
            const: "1",
            title: "Option A",
          },
          {
            const: "2",
            title: "Option B",
          },
          {
            const: "3",
            title: "Option C",
          },
        ],
      }),
    )

    return <SelectField state={state as FieldState<string | string[]>} />
  },
}

export const Radio: StoryObj<typeof SelectField> = {
  render() {
    const [[state]] = useState(() =>
      createState({
        title: "Select",
        "x-component": "radio",
        oneOf: [
          {
            const: "1",
            title: "Option A",
          },
          {
            const: "2",
            title: "Option B",
          },
          {
            const: "3",
            title: "Option C",
          },
        ],
      }),
    )

    return <SelectField state={state as FieldState<string | string[]>} />
  },
}

export const Checkbox: StoryObj<typeof SelectField> = {
  render() {
    const [[state]] = useState(() =>
      createState({
        type: "array",
        title: "Select",
        "x-component": "checkbox",
        items: {
          oneOf: [
            {
              const: "1",
              title: "Option A",
            },
            {
              const: "2",
              title: "Option B",
            },
            {
              const: "3",
              title: "Option C",
            },
          ],
        },
        minItems: 1,
        maxItems: 2,
        uniqueItems: true,
      }),
    )

    return <SelectField state={state as FieldState<string | string[]>} />
  },
}
