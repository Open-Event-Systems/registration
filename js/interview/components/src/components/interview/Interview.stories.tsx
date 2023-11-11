import { Interview } from "#src/components/interview/Interview"
import { Step } from "#src/components/interview/Step"
import { Box, LoadingOverlay } from "@mantine/core"
import {
  InterviewAPI,
  InterviewRecordStore,
  InterviewStateRecord,
  JSONSchema,
} from "@open-event-systems/interview-lib"
import { Meta, StoryObj } from "@storybook/react"
import { makeAutoObservable, observable } from "mobx"
import { useState } from "react"

const meta: Meta<typeof Interview> = {
  component: Interview,
  decorators: [
    (Story) => (
      <Box maw={300} pos="relative">
        <Story />
      </Box>
    ),
  ],
}

export default meta

class MockStore implements InterviewRecordStore {
  records = new Map<string, InterviewStateRecord>()

  constructor() {
    this.records.set("0", {
      id: "0",
      fieldValues: {
        field_0: "stored",
      },
      metadata: {},
      stateResponse: {
        state: "0",
        update_url: "/",
        content: {
          type: "question",
          schema: question1,
        },
      },
    })
    makeAutoObservable(this, {
      records: observable.shallow,
    })
  }

  getRecord(id: string): InterviewStateRecord | undefined {
    return this.records.get(id)
  }

  saveRecord(record: InterviewStateRecord): void {
    this.records.set(record.id, record)
  }
}

const question1: JSONSchema = {
  type: "object",
  title: "Name",
  description: "Enter your name.",
  properties: {
    field_0: {
      type: "string",
      "x-type": "text",
      minLength: 2,
      maxLength: 16,
      title: "Name",
    },
  },
  required: ["field_0"],
}

const question2: JSONSchema = {
  type: "object",
  title: "Question 2",
  description: "Choose the next step.",
  properties: {
    field_0: {
      "x-type": "select",
      "x-component": "radio",
      oneOf: [
        {
          const: "exit",
          title: "Exit",
        },
        {
          const: "error",
          title: "Error",
        },
      ],
    },
  },
  required: ["field_0"],
}

const mockAPI: InterviewAPI = {
  async updateState(record, responses) {
    await new Promise((r) => window.setTimeout(r, 1000))
    switch (record.id) {
      case "0":
        return {
          id: "1",
          fieldValues: {},
          metadata: { ...record.metadata },
          stateResponse: {
            state: "1",
            update_url: "/",
            content: {
              type: "question",
              schema: question2,
            },
          },
        }
      case "1":
        if (responses?.field_0 == "exit") {
          return {
            id: "2",
            fieldValues: {},
            metadata: { ...record.metadata },
            stateResponse: {
              state: "2",
              content: {
                type: "exit",
                title: "Exit Step",
                description: "This is the exit step.",
              },
            },
          }
        } else {
          return {
            id: "error",
            fieldValues: {},
            metadata: { ...record.metadata },
            stateResponse: {
              state: "error",
              content: {
                type: "error",
                description: "An error occurred. Please try again later.",
              },
            },
          }
        }
      default:
        throw new Error("Missing state")
    }
  },
}

export const Default: StoryObj<typeof Interview> = {
  render() {
    const [store] = useState(() => new MockStore())
    const [recordId, setRecordId] = useState("0")

    return (
      <Interview
        store={store}
        api={mockAPI}
        recordId={recordId}
        onNewRecord={(r) => {
          setRecordId(r.id)
        }}
        onClose={() => {
          setRecordId("0")
        }}
        render={({ record, onSubmit, onClose, submitting }) => {
          let content
          if (record && "content" in record.stateResponse) {
            content = (
              <Step
                key={record.id}
                content={record.stateResponse.content}
                initialValue={record.fieldValues}
                onSubmit={onSubmit}
                onClose={onClose}
              />
            )
          }

          return (
            <>
              {content}
              <LoadingOverlay visible={submitting} />
            </>
          )
        }}
      />
    )
  },
}
