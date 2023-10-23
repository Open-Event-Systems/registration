import { Wretch } from "wretch"
import wretch from "wretch"
import {
  FormValues,
  InterviewStateMetadata,
  InterviewStateRecord,
  StateResponse,
} from "#src/types.js"

const SESSION_STORAGE_KEY = "interview-state-v1"
const MAX_RECORDS = 50

/**
 * Indicates an error with the interview state.
 */
export class InterviewStateError extends Error {}

/**
 * Used to store interview states.
 */
export class InterviewStateRecordImpl {
  constructor(
    public stateResponse: StateResponse,
    public fieldValues: FormValues,
    public metadata: InterviewStateMetadata,
  ) {}

  /**
   * An identifier for this state record.
   *
   * We just take the first 32 characters of the state string, which should be unique
   * enough.
   */
  get id(): string {
    return this.stateResponse.state.substring(0, 32)
  }
}

/**
 * Manages interview state storage.
 */
export class InterviewStateStore {
  private wretch: Wretch
  private records = new Map<string, InterviewStateRecordImpl>()

  /**
   * Construct a new interview state store.
   * @param wretchInst - the {@link Wretch} instance
   */
  constructor(wretchInst?: Wretch) {
    if (wretchInst != null) {
      this.wretch = wretchInst
    } else {
      this.wretch = wretch()
    }

    this.load()
  }

  /**
   * Save the state records to session storage.
   */
  save() {
    const obj = Array.from(this.records.values(), (record) => ({
      r: record.stateResponse,
      v: record.fieldValues,
      m: record.metadata,
    }))

    const objStr = JSON.stringify(obj)
    window.sessionStorage.setItem(SESSION_STORAGE_KEY, objStr)
  }

  /**
   * Load the state records from the session store.
   */
  load() {
    const objStr = window.sessionStorage.getItem(SESSION_STORAGE_KEY)
    if (objStr) {
      try {
        const obj: {
          r: StateResponse
          v: FormValues
          m: InterviewStateMetadata
        }[] = JSON.parse(objStr)
        this.records.clear()
        obj.forEach((recordData) => {
          const record = new InterviewStateRecordImpl(
            recordData.r,
            recordData.v,
            recordData.m,
          )
          this.records.set(record.id, record)
        })
      } catch (_err) {
        // ignore
      }
    }
  }

  /**
   * Trim the number of saved state records.
   */
  trim() {
    if (this.records.size > MAX_RECORDS) {
      const numToRemove = this.records.size - MAX_RECORDS
      const removeIDs = []

      for (const id of this.records.keys()) {
        removeIDs.push(id)
        if (removeIDs.length == numToRemove) {
          break
        }
      }

      for (const id of removeIDs) {
        this.records.delete(id)
      }
    }
  }

  /**
   * Save a state record.
   * @param record - the record to save
   */
  saveRecord(record: InterviewStateRecord) {
    this.records.set(record.id, record)
    this.trim()
    this.save()
  }

  /**
   * Get a state record by ID.
   * @param id - the state ID
   * @returns the record, or undefined
   */
  getRecord(id: string): InterviewStateRecord | undefined {
    return this.records.get(id)
  }

  /**
   * Get an updated interview state.
   * @param record - the current record
   * @param responses - the form responses
   * @returns a new interview state record
   */
  private async updateState(
    record: InterviewStateRecordImpl,
    responses?: FormValues,
  ): Promise<InterviewStateRecordImpl> {
    const curStateResponse = record.stateResponse

    if (!("update_url" in curStateResponse)) {
      throw new Error("Interview state must be updatable")
    }

    const body = {
      state: record.stateResponse.state,
      responses: responses,
    }

    // TODO: better error handling
    const res = await this.wretch
      .url(curStateResponse.update_url, true)
      .json(body)
      .post()
      .badRequest(() => {
        throw new InterviewStateError()
      })
      .error(422, () => {
        throw new InterviewStateError()
      })
      .json<StateResponse>()

    const newRecord = new InterviewStateRecordImpl(
      res,
      {},
      { ...record.metadata },
    )
    this.saveRecord(newRecord)
    return newRecord
  }

  /**
   * Keep updating the interview state until it returns a result or is complete.
   *
   * This basically just handles an initial, empty state with no content.
   *
   * @param record - the state record
   * @returns a state record that is complete, or has content
   */
  private async advanceState(
    record: InterviewStateRecordImpl,
  ): Promise<InterviewStateRecordImpl> {
    let curRecord = record
    while (
      "update_url" in curRecord.stateResponse &&
      curRecord.stateResponse.content == null
    ) {
      const updated = await this.updateState(curRecord)
      curRecord = updated
    }
    return curRecord
  }

  /**
   * Start an interview from the initially received state.
   * @param response - the initial state response
   * @returns the next state record
   */
  async startInterview(
    response: StateResponse,
    metadata?: InterviewStateMetadata,
  ): Promise<InterviewStateRecord> {
    const record = new InterviewStateRecordImpl(response, {}, { ...metadata })
    this.saveRecord(record)

    const updated = await this.advanceState(record)

    return updated
  }

  /**
   * Update the interview process.
   * @param record - the current interview state
   * @param responses - the user's responses
   * @returns the next state record
   */
  async updateInterview(
    record: InterviewStateRecord,
    responses?: FormValues,
  ): Promise<InterviewStateRecord> {
    const updated = await this.updateState(record, responses)
    const withContent = await this.advanceState(updated)
    return withContent
  }
}
