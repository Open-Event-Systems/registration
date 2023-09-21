import { Meta, StoryObj } from "@storybook/react"
import { Box } from "@mantine/core"
import { QuestionView } from "#src/index.js"

export default {
  component: QuestionView,
} as Meta<typeof QuestionView>

const schema = {
  type: "object",
  title: "Example Question",
  description: "Example question with **markdown formatting**.",
  properties: {
    field_0: {
      type: "string",
      "x-type": "text",
      title: "First Name",
      "x-autocomplete": "given-name",
      minLength: 1,
      maxLength: 100,
    },
    field_1: {
      type: "string",
      "x-type": "text",
      title: "Last Name",
      "x-autocomplete": "family-name",
      minLength: 1,
      maxLength: 100,
    },
    field_2: {
      type: "integer",
      "x-type": "number",
      title: "Age",
      minimum: 0,
      maximum: 100,
      "x-input-mode": "numeric",
    },
    field_3: {
      type: "string",
      "x-type": "button",
      default: "2",
      oneOf: [
        {
          const: "1",
          title: "Other",
        },
        {
          const: "2",
          title: "Next",
          "x-primary": true,
        },
      ],
    },
  },
  required: ["field_0", "field_1", "field_2"],
}

export const Default: StoryObj<typeof QuestionView> = {
  args: {
    content: {
      type: "question",
      schema: schema,
    },
    initialValues: {
      field_1: "Initial Value",
    },
  },
  decorators: [
    (Story) => (
      <Box
        sx={{
          maxWidth: 350,
          border: "#000 dashed 1px",
          padding: 12,
          display: "flex",
          flexDirection: "column",
          alignItems: "stretch",
        }}
      >
        <Story />
      </Box>
    ),
  ],
  render(args) {
    return (
      <QuestionView
        sx={{ minHeight: 350, flex: "auto" }}
        {...args}
        onSubmit={async (v) => {
          await new Promise((r) => window.setTimeout(r, 1500))
          args.onSubmit(v)
        }}
      />
    )
  },
}
