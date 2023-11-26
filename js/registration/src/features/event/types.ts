import {
  DefinedInitialDataOptions,
  UseQueryOptions,
} from "@tanstack/react-query"

export interface Event {
  id: string
  name: string
  description?: string
  date: string
  open: boolean
  visible: boolean
  registration_options: RegistrationOption[]
}

export interface RegistrationOption {
  id: string
  name: string
  description?: string
}

export type EventAPI = {
  list(): DefinedInitialDataOptions<Map<string, Event>>
}
