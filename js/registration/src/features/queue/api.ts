import {
  QueueAPI,
  QueueItem,
  StationInfo,
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
    setStationSettings(stationId) {
      return {
        mutationKey: ["stations", stationId],
        async mutationFn(settings) {
          return await wretch
            .url(`/stations/${stationId}`)
            .json(settings)
            .put()
            .json<StationInfo>()
        },
        onSuccess(data) {
          queryClient.setQueryData(["stations", stationId], data)
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
    startQueueItem() {
      return {
        mutationKey: ["queue-items", "start"],
        async mutationFn(itemId) {
          let req = wretch.url(`/queue-items/${itemId}/start`)
          await req.put().res()
        },
      }
    },
    completeQueueItem() {
      return {
        mutationKey: ["queue-items", "complete"],
        async mutationFn({ itemId, registrationId }) {
          let req = wretch
            .url(`/queue-items/${itemId}/complete`)
            .addon(queryString)

          if (registrationId) {
            req = req.query({ registration_id: registrationId })
          }

          await req.put().res()
        },
        onSuccess(_data, { itemId }) {
          queryClient.setQueriesData<QueueItem[]>(
            { queryKey: ["queues"] },
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
    logQueueItem() {
      return {
        mutationKey: ["queue-items"],
        async mutationFn(data) {
          await wretch.url("/queue-items").json(data).post().res()
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
    createPrintRequest() {
      return {
        mutationKey: ["print-requests"],
        async mutationFn({ stationId, data }) {
          await wretch
            .url(`/stations/${stationId}/print-requests`)
            .json(data)
            .post()
            .res()
        },
      }
    },
    listPrintRequests(stationId) {
      return {
        queryKey: ["stations", stationId, "print-requests"],
        async queryFn() {
          return await wretch
            .url(`/stations/${stationId}/print-requests`)
            .get()
            .json<{ id: string; data: Record<string, unknown> }[]>()
        },
      }
    },
  }
}
