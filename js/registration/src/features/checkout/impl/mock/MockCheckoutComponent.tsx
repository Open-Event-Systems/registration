import { useCheckout } from "#src/features/checkout/hooks"
import { Button, Skeleton, Stack, TextInput } from "@mantine/core"
import { useLayoutEffect, useState } from "react"

declare module "#src/features/checkout/types/Checkout" {
  interface PaymentServiceMap {
    mock: Record<string, unknown>
  }
}

export const MockCheckoutComponent = () => {
  const { checkout, update, updating } = useCheckout()

  const [setupFinished, setSetupFinished] = useState(false)
  const [cardValue, setCardValue] = useState("")

  useLayoutEffect(() => {
    window.setTimeout(() => {
      setSetupFinished(true)
    }, 1500)
  }, [])

  if (!checkout || !setupFinished) {
    return <MockCheckoutComponent.Placeholder />
  }

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault()
        if (updating) {
          return
        }

        update({ card: cardValue })
      }}
    >
      <Stack>
        <TextInput
          name="card"
          placeholder="Mock Card #"
          inputMode="numeric"
          title="Card Number"
          value={cardValue}
          onChange={(e) => setCardValue(e.target.value)}
        />
        <Button type="submit" variant="filled">
          Pay
        </Button>
      </Stack>
    </form>
  )
}

MockCheckoutComponent.Placeholder = () => (
  <Stack>
    <Skeleton height="2.25rem" />
    <Skeleton height="2.25rem" />
  </Stack>
)
