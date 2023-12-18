import { Box, Button, Stack } from "@mantine/core"
import { BadgeData, Client, createClient } from "@open-event-systems/badge-lib"
import { useState } from "react"

export type BadgeProps = {
  badgeUrl: string
  badgeData: BadgeData
}

export const Badge = (props: BadgeProps) => {
  const { badgeUrl, badgeData } = props
  const [badgeAPI, setBadgeAPI] = useState<Client | null>(null)

  return (
    <Stack className="Badge-root">
      <Box className="Badge-container">
        <iframe
          className="Badge-frame"
          tabIndex={-1}
          onLoad={(e) => {
            const wnd = e.target as HTMLIFrameElement
            if (!wnd.contentWindow) {
              return
            }

            const origin = new URL(badgeUrl, window.location.href).origin
            setBadgeAPI(createClient(wnd.contentWindow, origin))
          }}
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
