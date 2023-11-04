import {
  FormValues,
  InterviewAPI,
  InterviewRecordStore,
  InterviewStateRecord,
  defaultAPI,
  updateInterview,
} from "@open-event-systems/interview-lib"
import { observer } from "mobx-react-lite"
import { ReactNode, useState } from "react"

export type InterviewProps = {
  store: InterviewRecordStore
  api?: InterviewAPI
  recordId?: string | null
  onNewRecord?: (record: InterviewStateRecord) => void
  onClose?: () => void
  render: (renderProps: {
    submitting: boolean
    record?: InterviewStateRecord
    onClose?: () => void
    onSubmit: (values: FormValues) => void
  }) => ReactNode
}

/**
 * Component that handles interview logic.
 */
export const Interview = observer((props: InterviewProps) => {
  const {
    store,
    api = defaultAPI,
    recordId,
    onNewRecord,
    onClose,
    render,
  } = props

  const record = recordId ? store.getRecord(recordId) : undefined
  const [submitting, setSubmitting] = useState(false)
  const handleSubmit = (values: FormValues) => {
    if (submitting || !record) {
      return
    }

    setSubmitting(true)
    updateInterview(store, api, record, values)
      .then((newRecord) => {
        onNewRecord && onNewRecord(newRecord)
        setSubmitting(false)
      })
      .catch((e) => {
        setSubmitting(false)
        throw e
      })
  }

  return render({
    submitting,
    record: record,
    onClose: onClose,
    onSubmit: handleSubmit,
  })
})

Interview.displayName = "Interview"
