import {
  DefinedInitialDataOptions,
  UndefinedInitialDataOptions,
} from "@tanstack/react-query"

export interface SelfServiceEvent {
  id: string
  name: string
  description?: string
  date: string
  open: boolean
}

export interface SelfServiceRegistration {
  id: string
  title?: string
  subtitle?: string
  description?: string
}

export interface InterviewOption {
  id: string
  name: string
}

export interface SelfServiceRegistrationResponse {
  registration: SelfServiceRegistration
  change_options: InterviewOption[]
}

export interface SelfServiceRegistrationListResponse {
  registrations: SelfServiceRegistrationResponse[]
  add_options: InterviewOption[]
}

declare module "#src/hooks/location" {
  interface LocationState {
    accessCodeDialogRegistrationId?: string
  }
}

export type SelfServiceAPI = {
  listEvents(): DefinedInitialDataOptions<Map<string, SelfServiceEvent>>
  listRegistrations(options?: {
    eventId?: string
    accessCode?: string
  }): DefinedInitialDataOptions<SelfServiceRegistrationListResponse>
  checkAccessCode(
    eventId: string,
    accessCode: string,
  ): UndefinedInitialDataOptions<boolean>
}
