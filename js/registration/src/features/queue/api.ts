import {
  QueueAPI,
  QueueItem,
  StationListResponse,
} from "#src/features/queue/types"
import { QueryClient } from "@tanstack/react-query"
import { Wretch } from "wretch"
import queryString from "wretch/addons/queryString"

export const createQueueAPI = (
  wretch: Wretch,
  queryClient: QueryClient,
): QueueAPI => {
  return {
    listStations() {
      return {
        queryKey: ["stations"],
        async queryFn() {
          return await wretch
            .url("/stations")
            .get()
            .json<StationListResponse[]>()
        },
        staleTime: 60000,
      }
    },
    getStation(stationId) {
      return {
        queryKey: ["stations", stationId],
        async queryFn() {
          return await wretch.url(`/stations/${stationId}`).get().json()
        },
      }
    },
    listQueueItems(groupId, stationId) {
      return {
        queryKey: ["queues", groupId, { stationId: stationId }],
        async queryFn() {
          let req = wretch.url(`/queues/${groupId}`).addon(queryString)

          if (stationId) {
            req = req.query({ station_id: stationId })
          }

          return await req.get().json<QueueItem[]>()
        },
      }
    },
    addQueueItem(groupId) {
      return {
        mutationKey: ["queues", groupId, "add"],
        async mutationFn({ scanData }) {
          const req = wretch
            .url(`/queues/${groupId}/add`)
            .json({ scan_data: scanData || null })
            .post()
            .json<QueueItem>()
          const res = await req
          return res
        },
        onSuccess(res) {
          queryClient.setQueryData<QueueItem[]>(
            ["queues", groupId, {}],
            (cur) => {
              if (!cur) {
                return [res]
              }

              const filtered = cur.filter((item) => item.id != res.id)
              filtered.push(res)
              return filtered
            },
          )
        },
      }
    },
    cancelQueueItem() {
      return {
        mutationKey: ["queue-items", "cancel"],
        async mutationFn(itemId) {
          await wretch.url(`/queue-items/${itemId}/cancel`).put()
        },
        onSuccess(_data, itemId) {
          queryClient.setQueriesData<QueueItem[]>(
            {
              queryKey: ["queues"],
            },
            (cur) => {
              if (!cur || !Array.isArray(cur)) {
                return
              }

              return cur.filter((item) => item.id != itemId)
            },
          )
        },
      }
    },
    solveQueue(groupId) {
      return {
        mutationKey: ["queues", groupId, "solve"],
        async mutationFn() {
          const req = wretch.url(`/queues/${groupId}/solve`).post()
          return await req.json<QueueItem[]>()
        },
        onSuccess(data) {
          const updateMap = new Map(data.map((item) => [item.id, item]))
          queryClient.setQueryData<QueueItem[]>(
            ["queues", groupId, {}],
            (cur) => {
              if (!cur) {
                return data
              }

              const newValues = cur.map((item) => {
                const updated = updateMap.get(item.id)
                return updated ?? item
              })
              return newValues
            },
          )
        },
      }
    },
  }
}
