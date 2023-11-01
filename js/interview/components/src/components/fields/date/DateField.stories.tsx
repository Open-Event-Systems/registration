import { DateField } from "#src/components/fields/date/DateField.js"
import { Box } from "@mantine/core"
import { FieldState, createState } from "@open-event-systems/interview-lib"
import { Meta, StoryObj } from "@storybook/react"
import { useState } from "react"

import "@mantine/dates/styles.css"

const meta: Meta<typeof DateField> = {
  component: DateField,
  decorators: [
    (Story) => (
      <Box maw={300}>
        <Story />
      </Box>
    ),
  ],
}

export default meta

export const Default: StoryObj<typeof DateField> = {
  render() {
    const [state] = useState(() =>
      createState({
        type: "string",
        title: "Date",
        format: "date",
        "x-minimum": "2000-01-01",
        "x-maximum": "2019-12-31",
      }),
    )

    return <DateField state={state as FieldState<string>} required />
  },
}
