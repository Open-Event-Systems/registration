import { ButtonList } from "#src/components/button-list/ButtonList.js"
import { ModalDialog } from "#src/components/dialog/ModalDialog.js"
import { Text } from "@mantine/core"
import { Meta, StoryObj } from "@storybook/react"

export default {
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
} as Meta<typeof ModalDialog>

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
