import { InterviewStateStore } from "@open-event-systems/interview-lib"
import { useState } from "react"
import { InterviewDialog } from "#src/components/interview/InterviewDialog.js"
import { Meta, StoryObj } from "@storybook/react"

export default {
  component: InterviewDialog,
} as Meta<typeof InterviewDialog>

const askResult = {
  type: "question",
  schema: {
    type: "object",
    properties: {
      field_0: {
        type: "string",
        "x-type": "text",
        title: "First Name",
        "x-autocomplete": "given-name",
        maxLength: 100,
      },
      field_1: {
        type: "string",
        "x-type": "text",
        title: "Last Name",
        "x-autocomplete": "family-name",
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
  },
}

const exitResult = {
  type: "exit",
  title: "Ineligible",
  description: "You are not eligible for this survey.",
}

export const Question: StoryObj<typeof InterviewDialog> = {
  args: {
    opened: true,
  },
  render(args) {
    const [stateStore] = useState(() => {
      const stateStore = new InterviewStateStore()

      stateStore.saveRecord({
        id: "0000",
        fieldValues: {},
        stateResponse: {
          content: askResult,
          state: "0000",
          update_url: "/",
        },
        metadata: {},
      })

      return stateStore
    })

    return <InterviewDialog {...args} recordId="0000" stateStore={stateStore} />
  },
}

export const Exit: StoryObj<typeof InterviewDialog> = {
  args: {
    opened: true,
  },
  render(args) {
    const [stateStore] = useState(() => {
      const stateStore = new InterviewStateStore()

      stateStore.saveRecord({
        id: "0001",
        fieldValues: {},
        stateResponse: {
          content: exitResult,
          state: "0001",
          update_url: "/",
        },
        metadata: {},
      })

      return stateStore
    })
    return <InterviewDialog {...args} recordId="0001" stateStore={stateStore} />
  },
}
