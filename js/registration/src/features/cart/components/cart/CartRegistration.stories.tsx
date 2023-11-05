import { CartRegistration } from "#src/features/cart/components/cart/CartRegistration.js"
import { LineItem } from "#src/features/cart/components/cart/LineItem.js"
import { Modifier } from "#src/features/cart/components/cart/Modifier.js"
import { Box } from "@mantine/core"
import { Meta, StoryObj } from "@storybook/react"

import "./Cart.module.css"

const meta: Meta<typeof CartRegistration> = {
  component: CartRegistration,
  decorators: [
    (Story) => (
      <Box
        style={{
          maxWidth: 800,
          border: "#ccc dashed 1px",
          padding: 16,
          display: "grid",
          gridTemplateColumns:
            "[icon-start] auto [ icon-end item-name-start item-description-start] 1fr [item-name-end item-description-end item-amount-start] auto [item-amount-end]",
          justifyItems: "end",
          alignItems: "baseline",
          columnGap: "16px",
        }}
      >
        <Story />
      </Box>
    ),
  ],
}

export default meta

export const Default: StoryObj<typeof CartRegistration> = {
  args: {
    name: "Example Registration",
    onRemove: undefined,
    children: [
      <LineItem
        key={1}
        name="Basic Registration"
        description="Basic registration which includes basic stuff."
        price={5000}
        modifiers={[
          <Modifier key={1} name="Early Bird Discount" amount={-500} />,
        ]}
      />,
      <LineItem
        key={2}
        name="VIP Upgrade"
        description="Add VIP status"
        price={2500}
      />,
    ],
  },
}

export const WithRemove: StoryObj<typeof CartRegistration> = {
  args: {
    name: "Example Registration",
    children: [
      <LineItem
        key={1}
        name="Basic Registration"
        description="Basic registration which includes basic stuff."
        price={5000}
        modifiers={[
          <Modifier key={1} name="Early Bird Discount" amount={-500} />,
        ]}
      />,
      <LineItem
        key={2}
        name="VIP Upgrade"
        description="Add VIP status"
        price={2500}
      />,
    ],
  },
}
