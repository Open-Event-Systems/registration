import {
  FormValues,
  InterviewStateStore,
} from "@open-event-systems/interview-lib"
import { observer } from "mobx-react-lite"
import { ExitView, ExitViewProps } from "#src/components/interview/ExitView.js"
import {
  QuestionView,
  QuestionViewProps,
} from "#src/components/interview/QuestionView.js"
import { ReactNode } from "react"

export type InterviewComponentProps = {
  /**
   * The current state record ID.
   */
  recordId: string

  /**
   * The {@link InterviewStateStore}.
   */
  stateStore: InterviewStateStore

  /**
   * The form submit handler.
   */
  onSubmit: (values: FormValues) => Promise<void>

  /**
   * Render function for a question.
   */
  renderQuestion?: (
    props: QuestionViewProps,
    title: string | undefined,
  ) => ReactNode

  /**
   * Render function for an exit result.
   */
  renderExit?: (props: ExitViewProps, title: string | undefined) => ReactNode
}

/**
 * A component to render interview content.
 */
export const InterviewComponent = observer((props: InterviewComponentProps) => {
  const {
    recordId,
    stateStore,
    onSubmit,
    renderQuestion = (props) => <QuestionView {...props} />,
    renderExit = (props) => <ExitView {...props} />,
  } = props

  const record = stateStore.getRecord(recordId)

  const content =
    record?.stateResponse.complete != true
      ? record?.stateResponse.content
      : null

  let children

  switch (content?.type) {
    case "question":
      children = renderQuestion(
        {
          onSubmit: onSubmit,
          content: content,
        },
        (content.schema.title as string) || "Question",
      )
      break
    case "exit":
      children = renderExit(
        {
          content: content,
        },
        content.title,
      )
      break
    default:
      children = null
      break
  }

  return <>{children}</>
})
