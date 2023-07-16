import { Dialog, DialogProps } from "#src/components/dialog/Dialog.js"
import { Meta, StoryFn } from "@storybook/react"

export default {
  component: Dialog,
  parameters: {
    layout: "fullscreen",
  },
} as Meta<typeof Dialog>

export const Default: StoryFn<typeof Dialog> = (args: DialogProps) => {
  return <Dialog {...args}>Dialog content.</Dialog>
}

Default.args = {
  opened: true,
  title: "Dialog Title",
  hideCloseButton: false,
  loading: false,
}
