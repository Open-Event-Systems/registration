import { Exit } from "#src/components/steps/exit/Exit"
import { Question } from "#src/components/steps/question/Question"
import {
  AskResult,
  FieldState,
  FormValues,
  ObjectFieldState,
  Result,
  createState,
} from "@open-event-systems/interview-lib"
import { useState } from "react"

export type StepProps = {
  content?: Result | null
  initialValue?: FormValues
  onSubmit?: (values: FormValues) => void
  onClose?: () => void
}

export const Step = (props: StepProps) => {
  const { content, initialValue, onSubmit, onClose } = props

  switch (content?.type) {
    case "question":
      return (
        <StepQuestion
          onSubmit={onSubmit}
          content={content}
          initialValue={initialValue}
        />
      )
    case "exit":
      return (
        <Exit content={content.description ?? undefined} onClose={onClose} />
      )
    case "error":
      return (
        <Exit content={content.description ?? undefined} onClose={onClose} />
      )
    default:
      return null
  }
}

const StepQuestion = ({
  content,
  initialValue,
  onSubmit,
}: {
  content: AskResult
  initialValue?: FormValues
  onSubmit?: (values: FormValues) => void
}) => {
  const [[fieldsState, getValidValue, buttonsState]] = useState(
    (): [
      ObjectFieldState,
      () => Record<string, unknown>,
      FieldState<string> | undefined,
    ] => {
      const [state, getValidValue] = createState(
        content.schema,
        initialValue,
      ) as [ObjectFieldState, () => Record<string, unknown>]
      let buttonsState

      // hacky, find/extract a button field state if there is one
      for (const [_, substate] of Object.entries(state.properties ?? {})) {
        if (substate?.schema["x-type"] == "button") {
          buttonsState = substate as FieldState<string>
          break
        }
      }

      return [state, getValidValue, buttonsState]
    },
  )

  const handleSubmit = () => {
    fieldsState.setTouched()
    if (!fieldsState.isValid) {
      return
    }

    onSubmit && onSubmit(getValidValue())
  }

  return (
    <Question
      onSubmit={() => {
        handleSubmit()
      }}
      content={fieldsState.schema.description}
      fieldsState={fieldsState}
      buttonsState={buttonsState}
    />
  )
}
