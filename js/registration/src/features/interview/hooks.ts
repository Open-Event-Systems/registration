import {
  InterviewRecordStore,
  makeInterviewRecordStore,
} from "@open-event-systems/interview-lib"
import { createContext, useContext } from "react"

export const InterviewRecordStoreContext = createContext<InterviewRecordStore>(
  makeInterviewRecordStore(),
)

export const useInterviewRecordStore = () =>
  useContext(InterviewRecordStoreContext)
