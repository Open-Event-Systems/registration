import { InterviewDialog } from "#src/features/interview/components/InterviewDialog.js"
import { InterviewStateStoreContext } from "#src/features/interview/hooks.js"
import { InterviewStateStore } from "@open-event-systems/interview-lib"
import { Meta, StoryObj } from "@storybook/react"
import { useState } from "react"

export default {
  component: InterviewDialog,
} as Meta<typeof InterviewDialog>

export const Empty: StoryObj<typeof InterviewDialog> = {
  args: {
    opened: true,
  },
  render: (args) => <InterviewDialog {...args} />,
}

export const Question: StoryObj<typeof InterviewDialog> = {
  args: {
    opened: true,
    recordId: "0000",
  },
  decorators: [
    (Story) => {
      const [state] = useState(() => {
        const store = new InterviewStateStore()

        store.records.set("0000", {
          id: "0000",
          stateResponse: {
            complete: false,
            content: {
              type: "question",
              schema: {
                type: "object",
                title: "Example Question",
                description: "An example question.",
                properties: {
                  field_0: {
                    type: "string",
                    title: "Name",
                    "x-type": "text",
                    minLength: 2,
                    maxLength: 20,
                  },
                },
                required: ["field_0"],
              },
            },
            state: "0000",
            update_url: "http://localhost",
          },
          fieldValues: {
            field_0: "Test",
          },
          metadata: {},
        })

        return store
      })
      return (
        <InterviewStateStoreContext.Provider value={state}>
          <Story />
        </InterviewStateStoreContext.Provider>
      )
    },
  ],
  render(args) {
    return (
      <InterviewDialog
        {...args}
        onSubmit={async (v) => {
          await new Promise((r) => window.setTimeout(r, 1000))
          await args.onSubmit(v)
        }}
      />
    )
  },
}

export const Exit: StoryObj<typeof InterviewDialog> = {
  args: {
    opened: true,
    recordId: "0001",
  },
  decorators: [
    (Story) => {
      const [state] = useState(() => {
        const store = new InterviewStateStore()

        store.records.set("0001", {
          id: "0001",
          stateResponse: {
            complete: false,
            content: {
              type: "exit",
              title: "Exit",
              description: "Example with an exit step.",
            },
            state: "0001",
            update_url: "http://localhost",
          },
          fieldValues: {
            field_0: "Test",
          },
          metadata: {},
        })

        return store
      })
      return (
        <InterviewStateStoreContext.Provider value={state}>
          <Story />
        </InterviewStateStoreContext.Provider>
      )
    },
  ],
  render(args) {
    return <InterviewDialog {...args} />
  },
}
