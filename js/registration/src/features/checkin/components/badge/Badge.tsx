import { Box, Button, Grid, Stack } from "@mantine/core"

export type BadgeProps = {
  badgeUrl: string
}

export const Badge = (props: BadgeProps) => {
  const { badgeUrl } = props
  return (
    <Stack className="Badge-root">
      <Box className="Badge-container">
        <iframe className="Badge-frame" tabIndex={-1} src={badgeUrl}></iframe>
      </Box>
      <Button variant="outline">Print</Button>
    </Stack>
  )
}
