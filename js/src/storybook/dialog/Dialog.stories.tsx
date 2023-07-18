import { Dialog, DialogProps } from "#src/components/dialog/Dialog.js"
import {
  DialogMenu,
  DialogMenuItem,
} from "#src/components/dialog/DialogMenu.js"
import { OptionsDialog } from "#src/components/dialog/OptionsDialog.js"
import { useDialog } from "#src/hooks/dialog.js"
import { Box, Button } from "@mantine/core"
import { Meta, StoryFn } from "@storybook/react"
import { RouterProvider, createMemoryRouter } from "react-router-dom"

export default {
  title: "Dialog/Dialog",
  parameters: {
    layout: "fullscreen",
  },
  decorators: [
    (Story) => {
      const router = createMemoryRouter([
        {
          path: "*",
          element: <Story />,
        },
      ])

      return <RouterProvider router={router} />
    },
  ],
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

export const Managed: StoryFn<{ id: string }> = ({ id }: { id: string }) => {
  const ManagedDialogComponent = useDialog(id)

  return (
    <>
      <Box p="1rem">
        <Button
          onClick={() => {
            ManagedDialogComponent.show()
          }}
        >
          Show Dialog
        </Button>
      </Box>
      <ManagedDialogComponent title="Managed Dialog">
        Dialog content.
      </ManagedDialogComponent>
    </>
  )
}

Managed.args = {
  id: "dialog",
}

export const ManagedOptions = () => {
  const ManagedDialogComponent = useDialog("withOptions", OptionsDialog)

  return (
    <>
      <Box p="1rem">
        <Button
          onClick={() => {
            ManagedDialogComponent.show()
          }}
        >
          Show Dialog
        </Button>
      </Box>
      <ManagedDialogComponent
        title="Managed Options Dialog"
        onSelect={() => {
          ManagedDialogComponent.close()
        }}
      >
        {[
          {
            id: "option1",
            label: "Option A",
          },
          {
            id: "option2",
            label: "Option B",
          },
          {
            id: "option3",
            label: "Option C",
          },
        ]}
      </ManagedDialogComponent>
    </>
  )
}

ManagedOptions.args = {
  id: "dialog",
}
