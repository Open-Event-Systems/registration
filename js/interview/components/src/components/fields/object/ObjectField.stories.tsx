import { ObjectField } from "#src/components/fields/object/ObjectField.js"
import { Box } from "@mantine/core"
import {
  ObjectFieldState,
  createState,
} from "@open-event-systems/interview-lib"
import { Meta, StoryObj } from "@storybook/react"
import { useState } from "react"

const meta: Meta<typeof ObjectField> = {
  component: ObjectField,
  decorators: [
    (Story) => (
      <Box maw={300}>
        <Story />
      </Box>
    ),
  ],
}

export default meta

export const Default: StoryObj<typeof ObjectField> = {
  render() {
    const [[state]] = useState(() =>
      createState({
        type: "object",
        properties: {
          field_0: {
            type: ["string", "null"],
            "x-type": "text",
            title: "Name",
            minLength: 2,
            maxLength: 10,
          },
          field_1: {
            type: "integer",
            "x-type": "number",
            title: "Age",
            minimum: 1,
            maximum: 100,
          },
          field_2: {
            type: "array",
            "x-type": "select",
            "x-component": "checkbox",
            title: "Option",
            items: {
              oneOf: [
                {
                  const: "1",
                  title: "Enable option",
                },
              ],
            },
            minItems: 0,
            maxItems: 1,
            uniqueItems: true,
          },
        },
        required: ["field_0", "field_1", "field_2"],
      }),
    )

    return <ObjectField state={state as ObjectFieldState} />
  },
}
