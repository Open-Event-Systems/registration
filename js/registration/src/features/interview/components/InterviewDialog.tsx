import {
  ModalDialog,
  ModalDialogProps,
} from "#src/components/dialog/ModalDialog.js"
import { useInterviewRecordStore } from "#src/features/interview/hooks.js"
import { useLocation, useNavigate } from "#src/hooks/location.js"
import { Interview, Step } from "@open-event-systems/interview-components"
import {
  InterviewAPI,
  InterviewStateRecord,
} from "@open-event-systems/interview-lib"
import { FormValues } from "@open-event-systems/interview-lib"
import { useRef } from "react"
import { WretchResponse } from "wretch"

export type InterviewDialogProps = {
  onSubmit?: (values: FormValues) => void
  onClose?: () => void
  submitting?: boolean
  record?: InterviewStateRecord
} & Omit<ModalDialogProps, "children" | "opened" | "onClose" | "onSubmit">

export const InterviewDialog = (props: InterviewDialogProps) => {
  const { onClose, onSubmit, submitting, record, ...other } = props

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
      styles={{
        body: {
          minHeight: 400,
          display: "flex",
          flexDirection: "column",
          alignItems: "stretch",
          "& > *": {
            flex: "auto",
          },
        },
      }}
      title={title}
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
    </ModalDialog>
  )
}

const Manager = (
  props: {
    api?: InterviewAPI
    onComplete: (
      response: Promise<WretchResponse>,
      record: InterviewStateRecord,
    ) => Promise<void>
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

  const handleNewRecord = (record: InterviewStateRecord) => {
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
