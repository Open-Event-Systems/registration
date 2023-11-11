import { ButtonList } from "#src/components/button-list/ButtonList"
import { ModalDialog } from "#src/components/dialog/ModalDialog"
import { Text } from "@mantine/core"
import { Meta, StoryObj } from "@storybook/react"

import "./ModalDialog.module.css"

const meta: Meta<typeof ModalDialog> = {
  component: ModalDialog,
  parameters: {
    layout: "fullscreen",
  },
  args: {
    title: "Dialog Title",
    opened: true,
    loading: false,
    hideCloseButton: false,
    noPadding: false,
  },
}

export default meta

export const Default: StoryObj<typeof ModalDialog> = {
  render: (args) => <ModalDialog {...args}>Dialog content.</ModalDialog>,
}

export const WithButtonList: StoryObj<typeof ModalDialog> = {
  render: (args) => (
    <ModalDialog {...args}>
      <Text component="p">Choose an option.</Text>
      <ButtonList>
        <ButtonList.Label>Change Registration</ButtonList.Label>
        <ButtonList.Button>Registration 1</ButtonList.Button>
        <ButtonList.Button>Registration 2</ButtonList.Button>
        <ButtonList.Divider />
        <ButtonList.Label>New Registration</ButtonList.Label>
        <ButtonList.Button>New Registration</ButtonList.Button>
      </ButtonList>
    </ModalDialog>
  ),
}
