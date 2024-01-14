import { useCheckout, useCheckoutAPI } from "#src/features/checkout/hooks"
import { Checkout, CheckoutState } from "#src/features/checkout/types/Checkout"
import { Stack, Text } from "@mantine/core"
import { useQueryClient } from "@tanstack/react-query"
import { useEffect } from "react"

declare module "#src/features/checkout/types/Checkout" {
  interface PaymentServiceMap {
    system: Record<string, never>
  }
}

export const SuspendCheckoutComponent = () => {
  const { checkout, setCompleteMessage } = useCheckout()
  const suspendCheckout = checkout as Checkout<"suspend">

  const queryClient = useQueryClient()
  const checkoutAPI = useCheckoutAPI()

  const completeMessage = (
    <Text>Proceed to a cashier to complete your checkout.</Text>
  )

  useEffect(() => {
    const updated = {
      ...suspendCheckout,
      state: CheckoutState.complete,
    }
    setCompleteMessage(completeMessage)
    queryClient.setQueryData(
      checkoutAPI.read(suspendCheckout.id).queryKey,
      updated,
    )
  }, [])

  return <Stack>{completeMessage}</Stack>
}
