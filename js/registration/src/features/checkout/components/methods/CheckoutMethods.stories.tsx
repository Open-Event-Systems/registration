import { ModalDialog } from "#src/components"
import { CheckoutMethods } from "#src/features/checkout/components/methods/CheckoutMethods"
import { Meta, StoryObj } from "@storybook/react"

const meta: Meta<typeof CheckoutMethods> = {
  component: CheckoutMethods,
}

export default meta

export const Default: StoryObj<typeof CheckoutMethods> = {
  args: {
    methods: [
      { method: "card", name: "Credit/Debit" },
      { method: "cash", name: "Cash" },
    ],
  },
  render(args) {
    return (
      <ModalDialog title="Checkout" opened>
        <CheckoutMethods {...args} />
      </ModalDialog>
    )
  },
}
