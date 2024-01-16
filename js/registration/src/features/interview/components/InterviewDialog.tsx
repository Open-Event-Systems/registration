import {
  ModalDialog,
  ModalDialogProps,
} from "#src/components/dialog/ModalDialog"
import { useInterviewRecordStore } from "#src/features/interview/hooks"
import { useLocation, useNavigate } from "#src/hooks/location"
import { LoadingOverlay } from "@mantine/core"
import { Interview, Step } from "@open-event-systems/interview-components"
import {
  InterviewAPI,
  InterviewStateRecord,
} from "@open-event-systems/interview-lib"
import { FormValues } from "@open-event-systems/interview-lib"
import clsx from "clsx"
import { useRef } from "react"

export type InterviewDialogProps = {
  onSubmit?: (values: FormValues) => void
  onClose?: () => void
  submitting?: boolean
  record?: InterviewStateRecord
} & Omit<ModalDialogProps, "children" | "opened" | "onClose" | "onSubmit">

export const InterviewDialog = (props: InterviewDialogProps) => {
  const { onClose, onSubmit, submitting, record, classNames, ...other } = props

  const prevRecord = useRef(record)

  const opened = !!record
  let title

  if (record) {
    prevRecord.current = record
  }

  const recordToShow = record ?? prevRecord.current

  let content

  if (recordToShow && !recordToShow.stateResponse.complete) {
    content = recordToShow.stateResponse.content
    if (content?.type == "question") {
      title =
        (typeof content.schema == "object"
          ? content.schema.title
          : undefined) || "Question"
    } else if (content?.type == "exit") {
      title = content.title
    } else if (content?.type == "error") {
      title = "Error"
    }
  }

  return (
    <ModalDialog
      opened={opened}
      onClose={onClose}
      classNames={{
        ...classNames,
        body: clsx("InterviewDialog-body", classNames?.body),
      }}
      title={title}
      closeOnClickOutside={false}
      closeOnEscape={false}
      {...other}
    >
      {content && recordToShow && (
        <Step
          key={recordToShow.id}
          content={content}
          initialValue={recordToShow.fieldValues}
          onClose={onClose}
          onSubmit={onSubmit}
        />
      )}
      <LoadingOverlay visible={submitting} />
    </ModalDialog>
  )
}

const Manager = (
  props: {
    api?: InterviewAPI
    onComplete: (record: InterviewStateRecord) => Promise<void>
  } & Omit<
    InterviewDialogProps,
    "onSubmit" | "onClose" | "submitting" | "record"
  >,
) => {
  const { onComplete, api, ...other } = props

  const loc = useLocation()
  const navigate = useNavigate()

  const interviewRecordStore = useInterviewRecordStore()
  const locState = loc.state?.showInterviewDialog
  const recordId = locState?.recordId

  const handleNewRecord = async (record: InterviewStateRecord) => {
    if (record.stateResponse.complete) {
      await (onComplete && onComplete(record))
    } else {
      navigate(loc, {
        state: {
          ...loc.state,
          showInterviewDialog: {
            eventId: record.metadata.eventId,
            recordId: record.id,
          },
        },
      })
    }
  }

  const handleClose = () => {
    navigate(loc, { state: { ...loc.state, showInterviewDialog: undefined } })
  }

  return (
    <Interview
      api={api}
      store={interviewRecordStore}
      onNewRecord={handleNewRecord}
      onClose={handleClose}
      recordId={recordId}
      render={({ record, submitting, onSubmit, onClose }) => {
        return (
          <InterviewDialog
            onSubmit={onSubmit}
            onClose={onClose}
            submitting={submitting}
            record={record}
            {...other}
          />
        )
      }}
    />
  )
}

InterviewDialog.Manager = Manager
