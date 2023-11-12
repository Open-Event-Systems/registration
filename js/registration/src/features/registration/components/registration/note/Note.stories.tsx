import {
  Note,
  NoteProps,
} from "#src/features/registration/components/registration/note/Note"
import { Box } from "@mantine/core"
import { Meta, StoryObj } from "@storybook/react"
import { ElementType, useState } from "react"

const meta: Meta<typeof Note> = {
  component: Note,
  parameters: {
    layout: "centered",
  },
  decorators: [
    (Story) => (
      <Box maw={500}>
        <Story />
      </Box>
    ),
  ],
}

export default meta

export const Default: StoryObj<
  ElementType<NoteProps & { editable?: boolean }>
> = {
  args: {
    editable: false,
  },
  render(args) {
    const [value, setValue] = useState("# Example\n\nExample note.\n")

    const { editable, ...other } = args

    return (
      <Note
        value={value}
        {...other}
        onChange={editable ? (v) => setValue(v) : undefined}
      />
    )
  },
}
