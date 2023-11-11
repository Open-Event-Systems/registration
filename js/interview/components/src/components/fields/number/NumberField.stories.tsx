import { NumberField } from "#src/components/fields/number/NumberField"
import { Box } from "@mantine/core"
import { FieldState, createState } from "@open-event-systems/interview-lib"
import { Meta, StoryObj } from "@storybook/react"
import { useState } from "react"

const meta: Meta<typeof NumberField> = {
  component: NumberField,
  decorators: [
    (Story) => (
      <Box maw={300}>
        <Story />
      </Box>
    ),
  ],
}

export default meta

export const Default: StoryObj<typeof NumberField> = {
  render() {
    const [[state]] = useState(() =>
      createState({
        type: "number",
        title: "Number",
        minimum: 0,
        maximum: 3,
      }),
    )

    return <NumberField state={state as FieldState<string | number>} />
  },
}
