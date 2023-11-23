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
  list(): Promise<Event[]>
}
