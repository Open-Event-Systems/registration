import { InterviewDialog } from "#src/features/interview/components/InterviewDialog.js"
import {
  InterviewRecordStoreContext,
  useInterviewRecordStore,
} from "#src/features/interview/hooks.js"
import { MantineProvider } from "@mantine/core"
import {
  InterviewRecordStore,
  InterviewStateRecord,
} from "@open-event-systems/interview-lib"
import { Meta, StoryObj } from "@storybook/react"
import { makeAutoObservable, observable } from "mobx"
import { useState } from "react"

const meta: Meta<typeof InterviewDialog> = {
  component: InterviewDialog,
  decorators: [
    (Story) => (
      <MantineProvider>
        <Story />
      </MantineProvider>
    ),
  ],
}

export default meta

export const Empty: StoryObj<typeof InterviewDialog> = {
  args: {},
  render: (args) => <InterviewDialog {...args} />,
}

class MockStore implements InterviewRecordStore {
  records = new Map<string, InterviewStateRecord>()

  constructor() {
    makeAutoObservable(this, {
      records: observable.ref,
    })
  }

  getRecord(id: string): InterviewStateRecord | undefined {
    return this.records.get(id)
  }

  saveRecord(record: InterviewStateRecord): void {
    this.records.set(record.id, record)
  }
}

export const Question: StoryObj<typeof InterviewDialog> = {
  decorators: [
    (Story) => {
      const [state] = useState(() => {
        const store = new MockStore()

        store.saveRecord({
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
        <InterviewRecordStoreContext.Provider value={state}>
          <Story />
        </InterviewRecordStoreContext.Provider>
      )
    },
  ],
  render(args) {
    const store = useInterviewRecordStore()
    return <InterviewDialog {...args} record={store.getRecord("0000")} />
  },
}

export const Exit: StoryObj<typeof InterviewDialog> = {
  decorators: [
    (Story) => {
      const [state] = useState(() => {
        const store = new MockStore()

        store.saveRecord({
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
        <InterviewRecordStoreContext.Provider value={state}>
          <Story />
        </InterviewRecordStoreContext.Provider>
      )
    },
  ],
  render(args) {
    const store = useInterviewRecordStore()
    return <InterviewDialog {...args} record={store.getRecord("0001")} />
  },
}
