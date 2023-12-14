/**
 * Badge data interface.
 */
export interface BadgeData {
  id: string
  event_id: string
  option_ids: string[]
  first_name?: string
  last_name?: string
  preferred_name?: string
  nickname?: string
  email?: string
  number?: number
  checked_in?: boolean
  check_in_count?: number
  [key: string]: unknown
}

export type FormatRequest = {
  type: "format"
  id: string
  data: BadgeData
}

export type PrintRequest = {
  type: "print"
  id: string
  data: BadgeData
}

export type FormatResponse = {
  id: string
}

export type PrintResponse = {
  id: string
}

export interface Client {
  format(data: BadgeData): Promise<void>
  print(data: BadgeData): Promise<void>
}

export interface Server {
  dispose(): void
}

export type FormatHandler = (data: BadgeData) => void | Promise<void>
export type PrintHandler = (data: BadgeData) => void | Promise<void>
