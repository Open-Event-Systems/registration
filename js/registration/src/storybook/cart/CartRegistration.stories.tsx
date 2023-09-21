import { CartRegistration } from "#src/features/cart/components/CartRegistration.js"
import { LineItem } from "#src/features/cart/components/LineItem.js"
import { Modifier } from "#src/features/cart/components/Modifier.js"
import { Box } from "@mantine/core"
import { Meta, StoryObj } from "@storybook/react"

export default {
  component: CartRegistration,
  decorators: [
    (Story) => (
      <Box
        sx={{
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
} as Meta<typeof CartRegistration>

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
