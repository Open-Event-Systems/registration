import { useCheckout } from "#src/features/checkout/hooks"
import { Checkout } from "#src/features/checkout/types/Checkout"
import { Box, Button, Stack, Text, TextInput } from "@mantine/core"
import { observer } from "mobx-react-lite"
import { FormEvent, useState } from "react"

export const SquareCashCheckoutComponent = observer(() => {
  const { id: checkoutId, update, checkout, setCompleteMessage } = useCheckout()

  const squareCheckout = checkout as Checkout<"square">
  const amount = squareCheckout.data.amount

  const [tenderedAmount, setTenderedAmount] = useState(0)

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    update({
      source_id: "CASH",
      cash_amount: tenderedAmount,
      idempotency_key: makeKey(checkoutId),
    }).then((res) => {
      if (res) {
        const squareCheckout = res as Checkout<"square">
        const fmtAmount = ((squareCheckout.data.change || 0) / 100).toFixed(2)
        setCompleteMessage(
          <Text component="p">
            Payment complete.
            <br />
            <strong>Change due: {fmtAmount}</strong>
          </Text>,
        )
      }
    })
  }

  let fmtTendered = tenderedAmount.toString()
  if (tenderedAmount < 10) {
    fmtTendered = "00" + fmtTendered
  } else if (tenderedAmount < 100) {
    fmtTendered = "0" + fmtTendered
  }
  fmtTendered =
    fmtTendered.slice(0, fmtTendered.length - 2) +
    "." +
    fmtTendered.slice(fmtTendered.length - 2)

  return (
    <Box component="form" onSubmit={handleSubmit}>
      <Stack>
        <Text component="p">
          Amount due: <strong>{amount}</strong>
        </Text>
        <TextInput
          label="Cash Tendered"
          value={fmtTendered}
          onChange={(e) => {
            const val = e.target.value.replace(/[^0-9]/g, "")
            const intVal = val ? parseInt(val) : 0
            setTenderedAmount(intVal)
          }}
        />
        <Button type="submit" variant="filled">
          Complete
        </Button>
      </Stack>
    </Box>
  )
})

SquareCashCheckoutComponent.displayName = "SquareCashCheckoutComponent"

// TODO: replace with a better ID function
const makeKey = (suffix: string) =>
  (Math.random().toString(36).substring(2) + suffix).substring(0, 45)
