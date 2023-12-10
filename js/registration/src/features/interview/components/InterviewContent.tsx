import { useInterviewRecordStore } from "#src/features/interview"
import { useLocation, useNavigate } from "#src/hooks/location"
import { Box, LoadingOverlay, Title } from "@mantine/core"
import { Interview, Step } from "@open-event-systems/interview-components"
import { FormValues, InterviewAPI } from "@open-event-systems/interview-lib"
import { InterviewStateRecord } from "@open-event-systems/interview-lib"

declare module "#src/hooks/location" {
  interface LocationState {
    showInterviewRecord?: string
  }
}

export type InterviewContentProps = {
  onSubmit?: (values: FormValues) => void
  onClose?: () => void
  submitting?: boolean
  record?: InterviewStateRecord
}

export const InterviewContent = (props: InterviewContentProps) => {
  const { onClose, onSubmit, submitting, record } = props

  let title

  let content

  if (record && !record.stateResponse.complete) {
    content = record.stateResponse.content
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
    <Box className="InterviewContent-root">
      <Title className="InterviewContent-title" order={3}>
        {title}
      </Title>
      {record && content && (
        <Step
          key={record.id}
          content={content}
          initialValue={record.fieldValues}
          onClose={onClose}
          onSubmit={onSubmit}
        />
      )}
      <LoadingOverlay visible={submitting} />
    </Box>
  )
}

const Manager = (props: {
  api?: InterviewAPI
  onComplete: (record: InterviewStateRecord) => Promise<void>
  onClose?: () => void
}) => {
  const { onComplete, api, onClose, ...other } = props

  const loc = useLocation()
  const navigate = useNavigate()

  const interviewRecordStore = useInterviewRecordStore()
  const recordId = loc.state?.showInterviewRecord

  const handleNewRecord = async (record: InterviewStateRecord) => {
    if (record.stateResponse.complete) {
      await (onComplete && onComplete(record))
    } else {
      navigate(loc, {
        state: {
          ...loc.state,
          showInterviewRecord: record.id,
        },
      })
    }
  }

  return (
    <Interview
      api={api}
      store={interviewRecordStore}
      onNewRecord={handleNewRecord}
      onClose={onClose}
      recordId={recordId}
      render={({ record, submitting, onSubmit, onClose }) => {
        return (
          <InterviewContent
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

InterviewContent.Manager = Manager
