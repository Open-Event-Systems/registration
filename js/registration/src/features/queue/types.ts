import {
  UndefinedInitialDataOptions,
  UseMutationOptions,
} from "@tanstack/react-query"

export type StationListResponse = {
  id: string
  group_id: string
}

export type QueueItem = {
  id: string
  date_created: string
  first_name?: string
  last_name?: string
  date_started?: string
  duration?: number
  station_id?: string
}

export type QueueAPI = {
  listStations: () => UndefinedInitialDataOptions<StationListResponse[]>
  listQueueItems: (groupId: string) => UndefinedInitialDataOptions<QueueItem[]>
  addQueueItem: (
    groupId: string,
  ) => UseMutationOptions<QueueItem, Error, { scanData?: string }>
  cancelQueueItem: () => UseMutationOptions<void, Error, string>
  solveQueue: (groupId: string) => UseMutationOptions<QueueItem[]>
}
