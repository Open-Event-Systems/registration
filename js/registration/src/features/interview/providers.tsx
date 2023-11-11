import { InterviewRecordStoreContext } from "#src/features/interview/hooks"
import { makeInterviewRecordStore } from "@open-event-systems/interview-lib"
import { ReactNode, useState } from "react"

export const InterviewRecordStoreProvider = ({
  children,
}: {
  children?: ReactNode
}) => {
  const [store] = useState(() => {
    const store = makeInterviewRecordStore()
    store.load()
    return store
  })

  return (
    <InterviewRecordStoreContext.Provider value={store}>
      {children}
    </InterviewRecordStoreContext.Provider>
  )
}
