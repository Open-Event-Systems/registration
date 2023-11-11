import {
  Receipt,
  receiptStyles,
} from "#src/features/receipt/components/Receipt"
import { Box, Global } from "@mantine/core"
import { Meta, StoryObj } from "@storybook/react"

export default {
  component: Receipt,
} as Meta<typeof Receipt>

export const Default: StoryObj<typeof Receipt> = {
  decorators: [
    (Story) => (
      <Box maw={500}>
        <Global styles={receiptStyles} />
        <Story />
      </Box>
    ),
  ],
  args: {
    receiptId: "ABCD1234AAAA",
    date: "2020-05-15 15:00:00",
    totalPrice: 11000,
  },
  render(args) {
    return (
      <Receipt {...args}>
        <Receipt.Registration
          name="Person 1"
          receiptUrl="http://registration.example.com/receipt/ABCD1234AAAA"
        >
          <Receipt.LineItem
            name="Standard"
            price={5000}
            description="Standard registration."
          >
            <Receipt.Modifier name="Early Bird Discount" amount={-500} />
          </Receipt.LineItem>
          <Receipt.LineItem
            name="VIP Upgrade"
            price={2500}
            description="Extra stuff"
          >
            <Receipt.Modifier name="Early Bird Discount" amount={-500} />
          </Receipt.LineItem>
        </Receipt.Registration>
        <Receipt.Divider />
        <Receipt.Registration
          name="Person 2"
          receiptUrl="http://registration.example.com/receipt/ABCD1234BBBB"
        >
          <Receipt.LineItem
            name="Standard"
            price={5000}
            description="Standard registration."
          >
            <Receipt.Modifier name="Early Bird Discount" amount={-500} />
          </Receipt.LineItem>
        </Receipt.Registration>
      </Receipt>
    )
  },
}
