import { useCheckout } from "#src/features/checkout/hooks"
import { Button, Stack, Text } from "@mantine/core"

declare module "#src/features/checkout/types/Checkout" {
  interface PaymentServiceMap {
    system: Record<string, never>
  }
}

export const SystemCheckoutComponent = () => {
  const { update } = useCheckout()

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault()
        update()
      }}
    >
      <Stack>
        <Text>No payment is due, you&apos;re all set!</Text>
        <Button type="submit" variant="filled">
          Complete
        </Button>
      </Stack>
    </form>
  )
}
