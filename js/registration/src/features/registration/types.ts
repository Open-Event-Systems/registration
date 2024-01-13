import { InterviewOption } from "#src/features/cart/types"
import {
  InterviewStateRecord,
  StateResponse,
} from "@open-event-systems/interview-lib"
import {
  UndefinedInitialDataInfiniteOptions,
  UndefinedInitialDataOptions,
  UseMutationOptions,
} from "@tanstack/react-query"

export enum RegistrationState {
  pending = "pending",
  created = "created",
  canceled = "canceled",
}

export interface RegistrationSearchResult {
  id: string
  state: RegistrationState
  event_id: string
  first_name?: string
  last_name?: string
  preferred_name?: string
  email?: string
  number?: number
}

export interface Registration {
  id: string
  state: RegistrationState
  event_id: string
  version: number
  date_created: string
  date_updated?: string

  number?: number
  option_ids: string[]
  email?: string
  first_name?: string
  last_name?: string
  preferred_name?: string
  birth_date?: string

  note?: string

  [prop: string]: unknown
}

export interface CreateRegistration {
  state: RegistrationState
  event_id: string

  number?: number
  option_ids: string[]
  email?: string
  first_name?: string
  last_name?: string
  preferred_name?: string

  [prop: string]: unknown
}

declare module "@open-event-systems/interview-lib" {
  interface InterviewStateMetadata {
    registrationId?: string
  }
}

export type RegistrationAPI = {
  list(
    query?: string,
    options?: { event_id?: string | null; all?: boolean },
  ): UndefinedInitialDataInfiniteOptions<RegistrationSearchResult[]>
  listAddInterviews(
    eventId: string,
  ): UndefinedInitialDataOptions<InterviewOption[]>
  readAddInterview(
    eventId: string,
    interviewId: string,
  ): UndefinedInitialDataOptions<StateResponse>
  read(id: string): UndefinedInitialDataOptions<Registration>
  update(): UseMutationOptions<Registration, Error, Registration>
  complete(id: string): UseMutationOptions<Registration, Error>
  cancel(id: string): UseMutationOptions<Registration, Error>
  listChangeInterviews(
    id: string,
  ): UndefinedInitialDataOptions<InterviewOption[]>
  readChangeInterview(
    id: string,
    interviewId: string,
  ): UndefinedInitialDataOptions<StateResponse>
  readCheckinInterview(
    id: string,
    stationId?: string,
  ): UndefinedInitialDataOptions<StateResponse>
  completeCheckinInterview(
    id: string,
  ): UseMutationOptions<void, Error, InterviewStateRecord>
}
