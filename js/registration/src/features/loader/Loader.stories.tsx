import {
  ManagedLoaderComponentProps,
  NotFoundError,
  createLoader,
} from "#src/features/loader"
import { Button, Skeleton, Stack, TextInput } from "@mantine/core"
import { Meta, StoryObj } from "@storybook/react"
import { ElementType, useMemo, useState } from "react"

const meta: Meta<ElementType<ManagedLoaderComponentProps<string>>> = {
  title: "features/loader/Loader",
}

export default meta

export const Default: StoryObj<
  ElementType<ManagedLoaderComponentProps<string>>
> = {
  render() {
    const [text, setText] = useState("default")
    const loader = useMemo(
      () =>
        createLoader(async () => {
          await new Promise((r) => window.setTimeout(r, 1500))
          if (text) {
            return text
          } else {
            throw new NotFoundError()
          }
        }),
      [text],
    )

    return (
      <Stack>
        <TextInput value={text} onChange={(e) => setText(e.target.value)} />
        <loader.Component
          placeholder={<Skeleton>Placeholder</Skeleton>}
          notFound={<>Not found</>}
        >
          {(value) => <>Text is {value}</>}
        </loader.Component>
      </Stack>
    )
  },
}
