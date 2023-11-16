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

export interface RegistrationAPI {
  search(
    query: string,
    options?: { after?: string },
  ): Promise<RegistrationSearchResult[]>
  create(registration: CreateRegistration): Promise<Registration>
  fromResponse(response: Response): Promise<Registration>
  read(id: string): Promise<Registration | undefined>
  update(registration: Registration): Promise<Registration>
  delete(id: string): Promise<void>
}
