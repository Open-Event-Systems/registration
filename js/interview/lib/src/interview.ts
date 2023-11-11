import { InterviewStateRecordImpl } from "#src/store"
import {
  FormValues,
  InterviewAPI,
  InterviewRecordStore,
  InterviewStateMetadata,
  InterviewStateRecord,
  StateResponse,
} from "#src/types"

/**
 * Keep updating the interview state until it returns a result or is complete.
 *
 * This basically just handles an initial, empty state with no content.
 *
 * @param api - the API object
 * @param record - the state record
 * @returns a state record that is complete, or has content
 */
const advanceState = async (
  api: InterviewAPI,
  record: InterviewStateRecord,
): Promise<InterviewStateRecord> => {
  let curRecord = record
  while (
    "update_url" in curRecord.stateResponse &&
    !curRecord.stateResponse.update_url &&
    curRecord.stateResponse.content == null
  ) {
    const updated = await api.updateState(curRecord)
    curRecord = updated
  }
  return curRecord
}

/**
 * Start an interview from the initially received state.
 *
 * @param store - the record store
 * @param api - the API object
 * @param response - the initial state response
 * @param metadata - metadata to store with the form state
 * @returns the next state record
 */
export const startInterview = async (
  store: InterviewRecordStore,
  api: InterviewAPI,
  response: StateResponse,
  metadata?: InterviewStateMetadata,
): Promise<InterviewStateRecord> => {
  const record = new InterviewStateRecordImpl(response, {}, { ...metadata })

  const updated = await advanceState(api, record)
  store.saveRecord(updated)
  return updated
}

/**
 * Update the interview process.
 *
 * Updates `record` with the provided responses, then saves both it and the new state.
 *
 * @param store - the record store
 * @param api - the API object
 * @param record - the current interview state record
 * @param responses - the user's responses
 * @returns the next state record
 */
export const updateInterview = async (
  store: InterviewRecordStore,
  api: InterviewAPI,
  record: InterviewStateRecord,
  responses?: FormValues,
): Promise<InterviewStateRecord> => {
  record.fieldValues = { ...responses }

  try {
    const updated = await api.updateState(record, responses)
    const withContent = await advanceState(api, updated)
    store.saveRecord(record)
    store.saveRecord(withContent)
    return withContent
  } catch (e) {
    store.saveRecord(record)
    throw e
  }
}
