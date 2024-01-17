import { useCheckInStore } from "#src/features/checkin/hooks"
import { useQueueAPI } from "#src/features/queue/hooks"
import { Box, Button, Group, Stack } from "@mantine/core"
import {
  BadgeData,
  Client,
  createClient,
  waitUntilReady,
} from "@open-event-systems/badge-lib"
import { useMutation, useQuery } from "@tanstack/react-query"
import { observer } from "mobx-react-lite"
import { useEffect, useRef, useState } from "react"

export type BadgeProps = {
  windowName?: string
  badgeUrl: string
  badgeData: BadgeData
}

export const Badge = observer((props: BadgeProps) => {
  const { windowName = "badge", badgeUrl, badgeData } = props
  const [badgeAPI, setBadgeAPI] = useState<Client | null>(null)
  const iframeRef = useRef<HTMLIFrameElement | null>(null)

  const checkInStore = useCheckInStore()
  const queueAPI = useQueueAPI()

  const stationInfo = useQuery({
    ...queueAPI.getStation(checkInStore.stationId ?? ""),
    staleTime: Infinity,
    enabled: !!checkInStore.stationId,
  })

  const delegatedPrint = useMutation(queueAPI.createPrintRequest())

  useEffect(() => {
    let cancel = false

    waitUntilReady(windowName).then(() => {
      if (!cancel && iframeRef.current?.contentWindow) {
        const origin = new URL(badgeUrl, window.location.href).origin
        setBadgeAPI(createClient(iframeRef.current.contentWindow, origin))
      }
    })

    return () => {
      cancel = true
    }
  }, [])

  // format the badge
  useEffect(() => {
    if (badgeAPI) {
      badgeAPI.format(badgeData)
    }
  }, [badgeAPI, badgeData])

  // auto print
  useEffect(() => {
    if (
      stationInfo.data?.settings.auto_print_url &&
      !checkInStore.printIds.has(badgeData.id)
    ) {
      checkInStore.print(stationInfo.data.settings.auto_print_url, badgeData)
    } else if (
      stationInfo.data?.settings.delegate_print_station &&
      !checkInStore.printIds.has(badgeData.id)
    ) {
      checkInStore.printIds.add(badgeData.id)
      delegatedPrint.mutate({
        stationId: stationInfo.data?.settings.delegate_print_station,
        data: badgeData,
      })
    }
  }, [badgeData.id])

  return (
    <Stack className="Badge-root">
      <Box className="Badge-container">
        <iframe
          key={badgeUrl}
          name={windowName}
          className="Badge-frame"
          tabIndex={-1}
          ref={iframeRef}
          src={badgeUrl}
        ></iframe>
      </Box>
      <Group>
        <Button
          variant="outline"
          onClick={() => {
            if (stationInfo.data?.settings.auto_print_url) {
              checkInStore.print(
                stationInfo.data.settings.auto_print_url,
                badgeData,
              )
            } else if (stationInfo.data?.settings.delegate_print_station) {
              checkInStore.printIds.add(badgeData.id)
              delegatedPrint.mutate({
                stationId: stationInfo.data?.settings.delegate_print_station,
                data: badgeData,
              })
            } else {
              badgeAPI && badgeAPI.print(badgeData ?? {})
            }
          }}
        >
          🖨️ Print
        </Button>
      </Group>
    </Stack>
  )
})

Badge.displayName = "Badge"
