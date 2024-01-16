import { Box, Title } from "@mantine/core"
import { ReactNode } from "react"

export type StationProps = {
  stationId?: string
  children?: ReactNode
}

export const Station = (props: StationProps) => {
  const { stationId, children } = props

  return (
    <Box className="Station-root">
      <Title order={6} className="Station-title">
        {stationId}
      </Title>
      {children}
    </Box>
  )
}
