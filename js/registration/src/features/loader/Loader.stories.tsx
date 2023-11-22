import { Await } from "#src/features/loader"
import { Button, Skeleton, Stack } from "@mantine/core"
import { Meta, StoryObj } from "@storybook/react"
import { useState } from "react"

const meta: Meta<typeof Await> = {
  component: Await,
}

export default meta

export const Default: StoryObj<typeof Await> = {
  render() {
    const [promise, setPromise] = useState<string | Promise<string>>(
      "first load",
    )

    return (
      <Stack>
        <Await value={promise} fallback={<Skeleton h={20} w={150} />}>
          {(value) => <>Loaded value: {value}</>}
        </Await>
        <Button
          maw={100}
          onClick={() => {
            const func = async () => {
              await new Promise((r) => window.setTimeout(r, 1500))
              return `Loaded at ${new Date()}`
            }
            setPromise(func())
          }}
        >
          Load
        </Button>
      </Stack>
    )
  },
}
