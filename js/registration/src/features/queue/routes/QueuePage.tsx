import { QueueItemComponent } from "#src/features/queue/components/item/QueueItem"
import { ScanInput } from "#src/features/queue/components/scan-input/ScanInput"
import { Station } from "#src/features/queue/components/station/Station"
import { useQueueAPI } from "#src/features/queue/hooks"
import { QueueItem } from "#src/features/queue/types"
import { Button, LoadingOverlay } from "@mantine/core"
import { useIsMutating, useMutation, useQuery } from "@tanstack/react-query"
import { useLayoutEffect, useRef, useState } from "react"
import { useParams } from "react-router-dom"

export const QueuePage = () => {
  const { groupId = "" } = useParams()

  const queueAPI = useQueueAPI()
  const allStations = useQuery(queueAPI.listStations())
  const stations = allStations.isSuccess
    ? allStations.data.filter((s) => s.group_id == groupId)
    : []

  const [bufferItemIds, setBufferItemIds] = useState(new Set<string>())

  const queueItems = useQuery({
    ...queueAPI.listQueueItems(groupId),
    refetchInterval: 5000,
  })

  useLayoutEffect(() => {
    const newIds = new Set(bufferItemIds)
    queueItems.data?.forEach((item) => {
      if (!item.station_id) {
        newIds.add(item.id)
      }
    })
    setBufferItemIds(newIds)
  }, [queueItems.data])

  const unassignedItems: QueueItem[] = []
  const queueItemsByStation = new Map<string, QueueItem[]>(
    stations.map((s) => [s.id, []]),
  )
  queueItems.data?.forEach((item) => {
    const stationList = item.station_id
      ? queueItemsByStation.get(item.station_id)
      : undefined
    if (stationList) {
      stationList.push(item)
    }

    if (!item.station_id) {
      unassignedItems.push(item)
    }
  })

  const add = useMutation(queueAPI.addQueueItem(groupId))
  const solve = useMutation(queueAPI.solveQueue(groupId))
  const remove = useMutation(queueAPI.cancelQueueItem())

  const mutatingQueue = useIsMutating({ mutationKey: ["queues", groupId] })
  const mutatingItems = useIsMutating({ mutationKey: ["queue-items"] })

  const mutating = mutatingQueue + mutatingItems > 0

  const scanInputRef = useRef<HTMLInputElement | null>(null)

  return (
    <>
      <ScanInput
        onScan={(value) => {
          add.mutate({ scanData: value })
        }}
        inputRef={scanInputRef}
      />
      <Button
        onClick={() => {
          if (!mutating) {
            solve.mutate()
          }
          scanInputRef.current?.focus({ preventScroll: true })
        }}
      >
        Solve
      </Button>
      <Station stationId="Queue">
        {queueItems.data
          ?.filter(
            (item) =>
              unassignedItems.includes(item) || bufferItemIds.has(item.id),
          )
          .reverse()
          .map((item) => (
            <QueueItemComponent
              key={item.id}
              queueItem={item}
              canHide={!!item.station_id}
              onHide={() => {
                const newSet = new Set(bufferItemIds)
                newSet.delete(item.id)
                setBufferItemIds(newSet)
                scanInputRef.current?.focus({ preventScroll: true })
              }}
              onRemove={() => {
                if (!mutating) {
                  remove.mutate(item.id)
                }
                scanInputRef.current?.focus({ preventScroll: true })
              }}
            />
          ))}
      </Station>
      {stations.map((s) => {
        const items = queueItemsByStation
          .get(s.id)
          ?.filter((item) => !bufferItemIds.has(item.id))
          .map((item) => (
            <QueueItemComponent
              key={item.id}
              queueItem={item}
              onRemove={() => {
                if (!mutating) {
                  remove.mutate(item.id)
                }
                scanInputRef.current?.focus({ preventScroll: true })
              }}
            />
          ))
        return (
          <Station key={s.id} stationId={`Station ${s.id}`}>
            {items}
          </Station>
        )
      })}
      <LoadingOverlay visible={mutating} />
    </>
  )
}
