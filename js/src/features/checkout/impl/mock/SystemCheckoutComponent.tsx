import { CheckoutState } from "#src/features/checkout/CheckoutState.js"
import { Button, Stack, Text } from "@mantine/core"
import { useEffect } from "react"

declare module "#src/features/checkout/types/Checkout.js" {
  interface PaymentServiceMap {
    system: Record<string, never>
  }
}

export type SystemCheckoutComponentProps = {
  state: CheckoutState<"system">
}

export const SystemCheckoutComponent = ({
  state,
}: SystemCheckoutComponentProps) => {
  const paymentHandler = async () => {
    // backend rejects an empty {}...
    await state.updateFunc({ complete: true })
  }

  useEffect(() => {
    state.clearLoading()
  }, [])

  return (
    <form onSubmit={(e) => e.preventDefault()}>
      <Stack>
        <Text>No payment is due, you&apos;re all set!</Text>
        <Button
          onClick={() => {
            if (state.loading) {
              return
            }
            state.wrapPromise(paymentHandler())
          }}
        >
          Complete
        </Button>
      </Stack>
    </form>
  )
}
