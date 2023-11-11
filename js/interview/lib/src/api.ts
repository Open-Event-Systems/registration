import { InterviewStateRecordImpl } from "#src/store"
import {
  ErrorResult,
  InterviewAPI,
  InterviewStateRecord,
  StateRequest,
  StateResponse,
} from "#src/types"

/**
 * Default API implementation.
 */
export const defaultAPI: InterviewAPI = {
  async updateState(record, responses) {
    if (
      !("update_url" in record.stateResponse) ||
      !record.stateResponse.update_url
    ) {
      throw new Error("Interview state must be updatable")
    }

    const body: StateRequest = {
      state: record.stateResponse.state,
      responses: responses,
    }

    const res = await fetch(record.stateResponse.update_url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
      mode: "cors",
      credentials: "include",
    })

    // TODO: more detailed error handling
    if (res.status == 422) {
      await res.text().catch()
      return makeErrorState(
        record,
        "The responses you provided were invalid. Please go back and correct your input.",
      )
    } else if (res.status == 400) {
      await res.text().catch()
      return makeErrorState(
        record,
        "Your responses could not be submitted. " +
          "The form you are using may have expired or been changed, " +
          "and you may need to restart the form.",
      )
    } else if (!res.ok) {
      await res.text().catch()
      return makeErrorState(record)
    }

    const resJson: StateResponse = await res.json()
    return new InterviewStateRecordImpl(resJson, {}, { ...record.metadata })
  },
}

const makeErrorState = (
  curRecord: InterviewStateRecord,
  msg?: string,
): InterviewStateRecord => {
  return {
    id: "error",
    fieldValues: {},
    metadata: { ...curRecord.metadata },
    stateResponse: {
      state: "error",
      content: makeErrorResult(msg),
    },
  }
}

const makeErrorResult = (msg?: string): ErrorResult => ({
  type: "error",
  description:
    msg || "An error occurred. Please go back and try your submission again.",
})
