import { CheckoutDialog } from "#src/features/checkout/components/checkout/CheckoutDialog"
import { Button, TextInput } from "@mantine/core"
import { Meta, StoryObj } from "@storybook/react"

const meta: Meta<typeof CheckoutDialog> = {
  component: CheckoutDialog,
}

export default meta

export const Default: StoryObj<typeof CheckoutDialog> = {
  render() {
    return (
      <CheckoutDialog opened title="Checkout">
        <TextInput placeholder="Card #" inputMode="numeric" />
        <Button variant="filled">Pay</Button>
      </CheckoutDialog>
    )
  },
}
