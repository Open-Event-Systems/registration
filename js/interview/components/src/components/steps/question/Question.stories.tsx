import { Question } from "#src/components/steps/question/Question"
import { Box } from "@mantine/core"
import {
  FieldState,
  ObjectFieldState,
  createState,
} from "@open-event-systems/interview-lib"
import { Meta, StoryObj } from "@storybook/react"
import { useState } from "react"

import "./Question.module.css"

const meta: Meta<typeof Question> = {
  component: Question,
}

export default meta

export const Default: StoryObj<typeof Question> = {
  decorators: [
    (Story) => (
      <Box maw={300}>
        <Story />
      </Box>
    ),
  ],
  render(args) {
    const [[fieldState]] = useState(() =>
      createState({
        type: "object",
        title: "Example Question",
        description: "This is an _example question_.",
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

    return <Question {...args} fieldsState={fieldState as ObjectFieldState} />
  },
}

export const With_Buttons: StoryObj<typeof Question> = {
  decorators: [
    (Story) => (
      <Box maw={300}>
        <Story />
      </Box>
    ),
  ],
  render(args) {
    const [[fieldState]] = useState(() =>
      createState({
        type: "object",
        title: "Example Question",
        description: "This is an _example question_.",
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

    const [[buttonState]] = useState(() =>
      createState({
        "x-type": "button",
        oneOf: [
          {
            const: "1",
            title: "Continue",
            "x-primary": true,
          },
          {
            const: "2",
            title: "Cancel",
          },
        ],
        default: "1",
      }),
    )

    return (
      <Question
        {...args}
        fieldsState={fieldState as ObjectFieldState}
        buttonsState={buttonState as FieldState<string>}
      />
    )
  },
}
