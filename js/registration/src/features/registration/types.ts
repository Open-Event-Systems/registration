import { CheckoutState } from "#src/features/checkout/types/Checkout"
import { PaginatedResult } from "#src/types/api"

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
    q?: string,
    options?: { all?: boolean; event_id?: string },
  ): Promise<PaginatedResult<RegistrationSearchResult[]>>
}
