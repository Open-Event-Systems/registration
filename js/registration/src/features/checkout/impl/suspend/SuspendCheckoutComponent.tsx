import { Stack, Text } from "@mantine/core"

declare module "#src/features/checkout/types/Checkout" {
  interface PaymentServiceMap {
    system: Record<string, never>
  }
}

export const SuspendCheckoutComponent = () => {
  return (
    <Stack>
      <Text>Proceed to a cashier to complete your checkout.</Text>
    </Stack>
  )
}
