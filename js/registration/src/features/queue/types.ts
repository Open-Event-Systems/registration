import {
  UndefinedInitialDataOptions,
  UseMutationOptions,
} from "@tanstack/react-query"

export type StationListResponse = {
  id: string
  group_id: string
}

export type StationInfo = {
  id: string
  group_id: string
  settings: StationSettings
}

export type StationSettings = {
  open: boolean
  max_queue_length: number
  tags: string[]
  delegate_print_station?: string
  auto_print_url?: string
}

export type QueueItem = {
  id: string
  date_created: string
  registration_id?: string
  first_name?: string
  preferred_name?: string
  last_name?: string
  date_started?: string
  duration?: number
  station_id?: string
}

export type LogQueueItemRequest = {
  station_id: string
  registration_id: string
  date_started: string
}

export type QueueAPI = {
  listStations: () => UndefinedInitialDataOptions<StationListResponse[]>
  getStation: (stationId: string) => UndefinedInitialDataOptions<StationInfo>
  setStationSettings: (
    stationId: string,
  ) => UseMutationOptions<StationInfo, Error, StationSettings>
  listQueueItems: (
    groupId: string,
    stationId?: string,
  ) => UndefinedInitialDataOptions<QueueItem[]>
  addQueueItem: (
    groupId: string,
  ) => UseMutationOptions<QueueItem, Error, { scanData?: string }>
  startQueueItem: () => UseMutationOptions<void, Error, string>
  completeQueueItem: () => UseMutationOptions<
    void,
    Error,
    { itemId: string; registrationId?: string }
  >
  logQueueItem: () => UseMutationOptions<void, Error, LogQueueItemRequest>
  cancelQueueItem: () => UseMutationOptions<void, Error, string>
  solveQueue: (groupId: string) => UseMutationOptions<QueueItem[]>
  createPrintRequest: () => UseMutationOptions<
    void,
    Error,
    { stationId: string; data: Record<string, unknown> }
  >
  listPrintRequests: (
    stationId: string,
  ) => UndefinedInitialDataOptions<
    { id: string; data: Record<string, unknown> }[]
  >
}
