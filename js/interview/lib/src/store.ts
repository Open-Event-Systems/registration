import {
  FormValues,
  InterviewRecordStore,
  InterviewStateMetadata,
  InterviewStateRecord,
  StateResponse,
} from "#src/types.js"
import { makeAutoObservable } from "mobx"

const SESSION_STORAGE_KEY = "interview-state-v1"
const MAX_RECORDS = 50

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

interface DefaultInterviewRecordStore extends InterviewRecordStore {
  /**
   * Save the state records to session storage.
   */
  save(): void

  /**
   * Load the state records from the session store.
   */
  load(): void
}

class InterviewRecordStoreImpl implements DefaultInterviewRecordStore {
  private records = new Map<string, InterviewStateRecordImpl>()
  constructor(
    private sessionStorageKey: string,
    private maxRecords: number,
  ) {
    makeAutoObservable<this, "sessionStorageKey" | "maxRecords">(this, {
      sessionStorageKey: false,
      maxRecords: false,
    })
  }

  save() {
    const obj = Array.from(this.records.values(), (record) => ({
      r: record.stateResponse,
      v: record.fieldValues,
      m: record.metadata,
    }))

    const objStr = JSON.stringify(obj)
    window.sessionStorage.setItem(this.sessionStorageKey, objStr)
  }

  load() {
    const objStr = window.sessionStorage.getItem(this.sessionStorageKey)
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
  private trim() {
    if (this.records.size > this.maxRecords) {
      const numToRemove = this.records.size - this.maxRecords
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

  getRecord(id: string): InterviewStateRecord | undefined {
    return this.records.get(id)
  }

  saveRecord(record: InterviewStateRecord): void {
    this.records.set(record.id, record)
    this.trim()
    this.save()
  }
}

/**
 * Create a {@link DefaultInterviewRecordStore}.
 * @param options - the options
 * @returns the store
 */
export const makeInterviewRecordStore = (options?: {
  sessionStorageKey?: string
  maxRecords?: number
}): DefaultInterviewRecordStore => {
  return new InterviewRecordStoreImpl(
    options?.sessionStorageKey ?? SESSION_STORAGE_KEY,
    options?.maxRecords ?? MAX_RECORDS,
  )
}
