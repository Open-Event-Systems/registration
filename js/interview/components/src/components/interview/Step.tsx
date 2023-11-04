import { Exit } from "#src/components/steps/exit/Exit.js"
import { Question } from "#src/components/steps/question/Question.js"
import {
  AskResult,
  FieldState,
  FormValues,
  InterviewStateRecord,
  InterviewStateStore,
  ObjectFieldState,
  Result,
  createState,
} from "@open-event-systems/interview-lib"
import { useState } from "react"

export type StepProps = {
  store: InterviewStateStore
  record: InterviewStateRecord
}

export const Step = (props: StepProps) => {
  const { store, record } = props
  const content = !record.stateResponse.complete
    ? record.stateResponse.content
    : undefined

  switch (content?.type) {
    case "question":
      return <StepQuestion store={store} content={content} />
    case "exit":
      return <Exit content={content.description ?? undefined} />
  }
}

const StepQuestion = ({
  store,
  record,
  content,
}: {
  store: InterviewStateStore
  record: InterviewStateRecord
  content: AskResult
}) => {
  const [[fieldsState, buttonsState]] = useState(
    (): [ObjectFieldState, FieldState<string> | undefined] => {
      const state = createState(content.schema) as ObjectFieldState
      let buttonsState

      // hacky, find/extract a button field state if there is one
      for (const [_, substate] of Object.entries(state.properties ?? {})) {
        if (substate?.schema["x-type"] == "button") {
          buttonsState = substate as FieldState<string>
          break
        }
      }

      return [state, buttonsState]
    },
  )

  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = () => {
    if (!fieldsState.isValid || submitting) {
      return
    }

    setSubmitting(true)
    try {
      // TODO: use validated values
      store.updateInterview(record, fieldsState.value as FormValues)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Question
      onSubmit={(e) => {
        e.preventDefault()
        handleSubmit()
      }}
      content={fieldsState.schema.description}
      fieldsState={fieldsState}
      buttonsState={buttonsState}
    />
  )
}
