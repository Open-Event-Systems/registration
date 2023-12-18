import { Box } from "@mantine/core"
import { ReactNode } from "react"

export const FullScreenLayout = ({ children }: { children?: ReactNode }) => {
  return <Box className="FullScreenLayout-root">{children}</Box>
}
