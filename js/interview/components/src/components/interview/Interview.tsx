import {
  InterviewStateRecord,
  InterviewStateStore,
} from "@open-event-systems/interview-lib"
import { observer } from "mobx-react-lite"
import { ReactNode } from "react"

export type InterviewProps = {
  store: InterviewStateStore
  recordId?: string | null
  render: (
    store: InterviewStateStore,
    record: InterviewStateRecord,
  ) => ReactNode
}

export const Interview = observer((props: InterviewProps) => {
  const { store, recordId, render } = props

  const record = recordId ? store.getRecord(recordId) : undefined

  if (record) {
    return render(store, record)
  } else {
    return null
  }
})

Interview.displayName = "Interview"
