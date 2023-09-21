import { useState } from "react"
import { Box, Stack, Text } from "@mantine/core"
import { DateField } from "#src/components/fields/DateField.js"
import { Observer } from "mobx-react-lite"
import { Meta, StoryObj } from "@storybook/react"
import { createState } from "@open-event-systems/interview-lib"

export default {
  component: DateField,
} as Meta<typeof DateField>

const today = new Date()

const pad = (v: number): string => {
  if (v < 10) {
    return `0${v}`
  } else {
    return `${v}`
  }
}

const schema = {
  type: "string",
  format: "date",
  title: "Birth Date",
  "x-minimum": "1900-01-01",
  "x-maximum": `${today.getFullYear()}-${pad(today.getMonth() + 1)}-${pad(
    today.getDate(),
  )}`,
  nullable: true,
  "x-type": "date",
}

export const Default: StoryObj<typeof DateField> = {
  render(args) {
    const [state] = useState(() => createState(schema))

    return (
      <Box sx={{ maxWidth: 300 }}>
        <Stack spacing="1rem">
          <DateField {...args} state={state} />
          <Observer>
            {() => (
              <Text>
                Result value: {(state.validValue as string) ?? "undefined"}
              </Text>
            )}
          </Observer>
        </Stack>
      </Box>
    )
  },
}
