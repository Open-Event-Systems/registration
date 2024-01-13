import { Box, Button, Stack } from "@mantine/core"
import {
  BadgeData,
  Client,
  createClient,
  waitUntilReady,
} from "@open-event-systems/badge-lib"
import { useEffect, useRef, useState } from "react"

export type BadgeProps = {
  windowName?: string
  badgeUrl: string
  badgeData: BadgeData
}

export const Badge = (props: BadgeProps) => {
  const { windowName = "badge", badgeUrl, badgeData } = props
  const [badgeAPI, setBadgeAPI] = useState<Client | null>(null)
  const iframeRef = useRef<HTMLIFrameElement | null>(null)

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

  return (
    <Stack className="Badge-root">
      <Box className="Badge-container">
        <iframe
          key={badgeUrl}
          name={windowName}
          className="Badge-frame"
          tabIndex={-1}
          ref={iframeRef}
          // onLoad={(e) => {
          //   const wnd = e.target as HTMLIFrameElement
          //   if (!wnd.contentWindow) {
          //     return
          //   }

          //   const origin = new URL(badgeUrl, window.location.href).origin
          //   setBadgeAPI(createClient(wnd.contentWindow, origin))
          // }}
          src={badgeUrl}
        ></iframe>
      </Box>
      <Button
        variant="outline"
        onClick={() => {
          badgeAPI && badgeAPI.print(badgeData ?? {})
        }}
      >
        🖨️ Print
      </Button>
    </Stack>
  )
}
