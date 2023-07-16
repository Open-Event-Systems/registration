import { Dialog, DialogProps } from "#src/components/dialog/Dialog.js"
import {
  DialogMenu,
  DialogMenuItem,
} from "#src/components/dialog/DialogMenu.js"
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
  noPadding: false,
}

export const WithMenu: StoryFn = () => {
  return (
    <Dialog opened hideCloseButton title="Select An Option" noPadding>
      <DialogMenu>
        <DialogMenuItem label="Option A" />
        <DialogMenuItem label="Option B" />
        <DialogMenuItem label="Option C" />
      </DialogMenu>
    </Dialog>
  )
}

export const WithMenuLinkComponent: StoryFn = () => {
  return (
    <Dialog opened hideCloseButton title="Select An Option" noPadding>
      <DialogMenu>
        <DialogMenuItem component="a" href="#" label="Option A" />
        <DialogMenuItem component="a" href="#" label="Option B" />
        <DialogMenuItem component="a" href="#" label="Option C" />
      </DialogMenu>
    </Dialog>
  )
}
