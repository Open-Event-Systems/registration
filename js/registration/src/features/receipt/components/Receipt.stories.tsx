import { Receipt } from "#src/features/receipt/components/Receipt"
import { Box } from "@mantine/core"
import { Meta, StoryObj } from "@storybook/react"

import "./Receipt.scss"

const meta: Meta<typeof Receipt> = {
  component: Receipt,
}

export default meta

export const Default: StoryObj<typeof Receipt> = {
  decorators: [
    (Story) => (
      <Box maw={500}>
        <Story />
      </Box>
    ),
  ],
  args: {
    receiptId: "ABCD1234AAAA",
    pricingResult: {
      date: "2020-05-15T15:00:00-04:00",
      currency: "USD",
      receipt_url: "http://localhost:6006/receipt/ABCD1234AAAA",
      registrations: [
        {
          registration_id: "r1",
          name: "Person 1",
          line_items: [
            {
              registration_id: "r1",
              name: "Standard",
              description: "Standard registration.",
              price: 5000,
              modifiers: [{ name: "Early Bird Discount", amount: -500 }],
              total_price: 4500,
            },
            {
              registration_id: "r1",
              name: "VIP Upgrade",
              description: "Extra stuff",
              price: 2500,
              modifiers: [{ name: "Early Bird Discount", amount: -500 }],
              total_price: 2000,
            },
          ],
        },
        {
          registration_id: "r2",
          name: "Person 2",
          line_items: [
            {
              registration_id: "r1",
              name: "Standard",
              description: "Standard registration.",
              price: 5000,
              modifiers: [{ name: "Early Bird Discount", amount: -500 }],
              total_price: 4500,
            },
          ],
        },
      ],
      modifiers: [],
      total_price: 11000,
    },
  },
  render(args) {
    return <Receipt {...args} />
  },
}
