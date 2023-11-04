import {
  FormValues,
  InterviewStateRecord,
  InterviewStateStore,
} from "@open-event-systems/interview-lib"
import { observer } from "mobx-react-lite"
import { ReactNode, useState } from "react"

export type InterviewProps = {
  store: InterviewStateStore
  recordId?: string | null
  onNewRecord?: (record: InterviewStateRecord) => void
  onUpdate?: (
    store: InterviewStateStore,
    record: InterviewStateRecord,
    responses?: FormValues,
  ) => Promise<InterviewStateRecord>
  render: (renderProps: {
    store: InterviewStateStore
    submitting: boolean
    record?: InterviewStateRecord
    onSubmit: (values: FormValues) => void
  }) => ReactNode
}

/**
 * Component that handles interview logic.
 */
export const Interview = observer((props: InterviewProps) => {
  const {
    store,
    recordId,
    onNewRecord,
    onUpdate = defaultHandleUpdate,
    render,
  } = props

  const record = recordId ? store.getRecord(recordId) : undefined
  const [submitting, setSubmitting] = useState(false)
  const handleSubmit = (values: FormValues) => {
    if (submitting || !record) {
      return
    }

    setSubmitting(true)
    onUpdate(store, record, values)
      .then((newRecord) => {
        onNewRecord && onNewRecord(newRecord)
        setSubmitting(false)
      })
      .catch(() => {
        // TODO: error handling here
        setSubmitting(false)
      })
  }

  return render({
    store,
    submitting,
    record: record,
    onSubmit: handleSubmit,
  })
})

Interview.displayName = "Interview"

const defaultHandleUpdate = async (
  store: InterviewStateStore,
  record: InterviewStateRecord,
  responses?: FormValues,
): Promise<InterviewStateRecord> => {
  return await store.updateInterview(record, responses)
}
