import {
  ModalDialog,
  ModalDialogProps,
} from "#src/components/dialog/ModalDialog.js"
import { useInterviewState } from "#src/features/interview/hooks.js"
import { useWretch } from "#src/hooks/api.js"
import { useLocation, useNavigate } from "#src/hooks/location.js"
import { Skeleton } from "@mantine/core"
import { ExitView } from "@open-event-systems/interview-components/components/interview/ExitView.js"
import { QuestionView } from "@open-event-systems/interview-components/components/interview/QuestionView.js"
import {
  AskResult,
  ExitResult,
  FormValues,
  InterviewStateRecord,
} from "@open-event-systems/interview-lib"
import { observer } from "mobx-react-lite"
import { ReactNode, useLayoutEffect, useState } from "react"
import { WretchResponse } from "wretch"

export type InterviewDialogProps = {
  recordId: string
  content?: AskResult | ExitResult | null
  onSubmit: (values: FormValues, button: number | null) => Promise<void>
} & Omit<ModalDialogProps, "children" | "onSubmit" | "content">

export const InterviewDialog = (props: InterviewDialogProps) => {
  const { recordId, opened, content, onClose, onSubmit, ...other } = props

  let title: ReactNode = <Skeleton height={24} width={120} />
  let contentEl

  if (content?.type == "exit") {
    title = content.title
    contentEl = <ExitView key={recordId} content={content} onClose={onClose} />
  } else if (content?.type == "question") {
    title = content.title || "Question"
    contentEl = (
      <QuestionView key={recordId} content={content} onSubmit={onSubmit} />
    )
  } else {
    contentEl = (
      <>
        <Skeleton height={24} mt={6} />
        <Skeleton height={24} mt={6} />
        <Skeleton height={150} mt={30} />
      </>
    )
  }

  return (
    <ModalDialog opened={opened} title={title} onClose={onClose} {...other}>
      {contentEl}
    </ModalDialog>
  )
}

const Manager = observer(
  (
    props: {
      onComplete: (
        response: Promise<WretchResponse>,
        record: InterviewStateRecord
      ) => Promise<void>
    } & Omit<InterviewDialogProps, "onSubmit" | "recordId">
  ) => {
    const { onComplete, ...other } = props

    const wretch = useWretch()
    const loc = useLocation()
    const navigate = useNavigate()

    const interviewState = useInterviewState()

    const locState = loc.state?.showInterviewDialog

    const record = locState?.recordId
      ? interviewState.getRecord(locState.recordId)
      : void 0

    const responseContent =
      !!record && !record.stateResponse.complete
        ? record.stateResponse.content
        : null

    const [prevContent, setPrevContent] = useState(responseContent)

    const show = !!locState?.recordId && !!record

    useLayoutEffect(() => {
      if (show) {
        setPrevContent(responseContent)
      }
    }, [responseContent, show])

    const handleClose = () => {
      navigate(loc, { state: { ...loc.state, showInterviewDialog: undefined } })
    }

    const handleSubmit = async (values: FormValues, button: number | null) => {
      if (!record || !locState) {
        return
      }

      const newRecord = await interviewState.updateInterview(
        record,
        values,
        button ?? void 0
      )
      if (newRecord.stateResponse.complete) {
        const target = newRecord.stateResponse.target_url
        const submitResponse = wretch
          .url(target, true)
          .json({
            state: newRecord.stateResponse.state,
          })
          .post()
          .res()

        onComplete(submitResponse, newRecord)
      } else {
        navigate(loc, {
          state: {
            ...loc.state,
            showInterviewDialog: {
              recordId: newRecord.id,
              eventId: locState.eventId,
            },
          },
        })
      }
    }

    return (
      <InterviewDialog
        {...other}
        recordId={record?.id ?? ""}
        opened={show}
        onClose={handleClose}
        onSubmit={handleSubmit}
        content={show ? responseContent : prevContent}
      />
    )
  }
)

Manager.displayName = "InterviewDialogManager"

InterviewDialog.Manager = Manager
