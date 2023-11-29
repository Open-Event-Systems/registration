import { CheckoutImplComponentProps } from "#src/features/checkout/components/checkout/CheckoutComponent"
import { Checkout } from "#src/features/checkout/types/Checkout"
import { Button, Skeleton, Stack, TextInput } from "@mantine/core"
import { useLayoutEffect, useState } from "react"

export type MockCheckoutComponentProps = CheckoutImplComponentProps<"mock">

export const MockCheckoutComponent = (props: MockCheckoutComponentProps) => {
  const { checkout } = props
  const [setupFinished, setSetupFinished] = useState(false)
  useLayoutEffect(() => {
    window.setTimeout(() => {
      setSetupFinished(true)
    }, 1500)
  }, [])

  if (!checkout || !setupFinished) {
    return <MockCheckoutComponent.Placeholder />
  } else {
    return <MockCheckoutComponent.Form {...props} checkout={checkout} />
  }
}

MockCheckoutComponent.Placeholder = () => (
  <Stack>
    <Skeleton height="2.25rem" />
    <Skeleton height="2.25rem" />
  </Stack>
)

MockCheckoutComponent.Form = (
  props: MockCheckoutComponentProps & { checkout: Checkout<"mock"> },
) => {
  const { update } = props
  const [value, setValue] = useState("")
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault()
        let card = parseInt(value)
        if (isNaN(card)) {
          card = 0
        }

        update({ card: card })
      }}
    >
      <Stack>
        <TextInput
          name="card"
          placeholder="Mock Card #"
          inputMode="numeric"
          title="Card Number"
          value={value}
          onChange={(e) => setValue(e.target.value)}
        />
        <Button type="submit" variant="filled">
          Pay
        </Button>
      </Stack>
    </form>
  )
}
