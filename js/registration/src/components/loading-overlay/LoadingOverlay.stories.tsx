import { LoadingOverlay } from "#src/components"
import { useShowLoading } from "#src/hooks/loader.js"
import { Box, Button } from "@mantine/core"
import { Meta, StoryObj } from "@storybook/react"

import "./LoadingOverlay.module.css"

const meta: Meta<typeof LoadingOverlay> = {
  component: LoadingOverlay,
  parameters: {
    layout: "fullscreen",
  },
}

export default meta

export const Default: StoryObj<typeof LoadingOverlay> = {
  render() {
    const showLoading = useShowLoading()

    return (
      <Box p={8}>
        <Button
          onClick={() => {
            const promise = new Promise((r) => window.setTimeout(r, 1500))
            showLoading(promise)
          }}
        >
          Load
        </Button>
        <LoadingOverlay />
      </Box>
    )
  },
}
