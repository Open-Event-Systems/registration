import { useCheckInStore } from "#src/features/checkin/hooks"
import { useQueueAPI } from "#src/features/queue/hooks"
import { Box, Button, Group, Select, Stack } from "@mantine/core"
import {
  BadgeData,
  Client,
  createClient,
  waitUntilReady,
} from "@open-event-systems/badge-lib"
import { useQuery } from "@tanstack/react-query"
import { action } from "mobx"
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

  const printers = useQuery({
    queryKey: ["printers"],
    async queryFn() {
      return await checkInStore.getPrinters(
        stationInfo.data?.settings.auto_print_url ?? "",
      )
    },
    staleTime: Infinity,
    enabled: !!stationInfo.data?.settings.auto_print_url,
  })

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
      checkInStore.printer &&
      !checkInStore.printIds.has(badgeData.id)
    ) {
      checkInStore.print(
        stationInfo.data.settings.auto_print_url,
        checkInStore.printer,
        badgeData,
      )
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
            if (
              stationInfo.data?.settings.auto_print_url &&
              checkInStore.printer
            ) {
              checkInStore.print(
                stationInfo.data.settings.auto_print_url,
                checkInStore.printer,
                badgeData,
              )
            } else {
              badgeAPI && badgeAPI.print(badgeData ?? {})
            }
          }}
        >
          🖨️ Print
        </Button>
        {!!stationInfo.data?.settings.auto_print_url && printers.isSuccess && (
          <Select
            placeholder="Printer"
            value={checkInStore.printer}
            data={
              printers.data?.map((p) => ({
                label: p.name,
                value: p.id,
              })) ?? []
            }
            onChange={action((value) => {
              checkInStore.printer = value
            })}
          />
        )}
      </Group>
    </Stack>
  )
})

Badge.displayName = "Badge"
