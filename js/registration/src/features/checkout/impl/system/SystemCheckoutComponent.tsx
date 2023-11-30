import { CheckoutImplComponentProps } from "#src/features/checkout/components/checkout/CheckoutComponent"
import { Button, Stack, Text } from "@mantine/core"

declare module "#src/features/checkout/types/Checkout" {
  interface PaymentServiceMap {
    system: Record<string, never>
  }
}

export type SystemCheckoutComponentProps = CheckoutImplComponentProps<"system">

export const SystemCheckoutComponent = (
  props: SystemCheckoutComponentProps,
) => {
  const { update } = props

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
