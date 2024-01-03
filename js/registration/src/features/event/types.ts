import {
  DefinedInitialDataOptions,
  UndefinedInitialDataOptions,
} from "@tanstack/react-query"

export interface Event {
  id: string
  name: string
  description?: string
  date: string
  open: boolean
  visible: boolean
  registration_options: RegistrationOption[]
  badge_url: string
}

export interface RegistrationOption {
  id: string
  name: string
  description?: string
}

export type EventAPI = {
  list(): DefinedInitialDataOptions<Map<string, Event>>
  read(eventId: string): UndefinedInitialDataOptions<Event>
}
