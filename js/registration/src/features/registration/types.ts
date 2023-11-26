import {
  UndefinedInitialDataInfiniteOptions,
  UndefinedInitialDataOptions,
  UseMutationOptions,
  UseQueryOptions,
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

export type RegistrationAPI = {
  list(
    query?: string,
    options?: { event_id?: string | null; all?: boolean },
  ): UndefinedInitialDataInfiniteOptions<RegistrationSearchResult[]>
  read(id: string): UndefinedInitialDataOptions<Registration>
  update(): UseMutationOptions<Registration, Error, Registration>
  complete(id: string): UseMutationOptions<Registration, Error>
  cancel(id: string): UseMutationOptions<Registration, Error>
}
