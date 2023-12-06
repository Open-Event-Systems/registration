import { Box } from "@mantine/core"
import { ReactNode } from "react"

export const FullScreenLayout = ({ children }: { children?: ReactNode }) => {
  return (
    <Box
      miw="100vw"
      mih="100vh"
      display="flex"
      style={{
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      {children}
    </Box>
  )
}
