import { CheckoutState } from "#src/features/checkout/CheckoutState.js"
import {
  SquareCheckout,
  loadSquare,
} from "#src/features/checkout/impl/square/SquareCheckout.js"
import { Box, Button, Stack } from "@mantine/core"
import type { Card } from "@square/web-payments-sdk-types"
import { useCallback, useEffect, useState } from "react"

export const SquareCheckoutComponent = ({
  state,
}: {
  state: CheckoutState<"square">
}) => {
  const [containerEl, setContainerEl] = useState<HTMLDivElement | null>(null)
  const containerElRef = useCallback(setContainerEl, [])

  const [square, setSquare] = useState<SquareCheckout | null>(null)
  const [card, setCard] = useState<Card | null>(null)
  const [ready, setReady] = useState(false)
  const [idempotencyKey, setIdempotencyKey] = useState(() => makeKey(state.id))
  const [submitting, setSubmitting] = useState(false)

  const checkoutData = state.data

  const handleSubmit = async () => {
    const cardVal = card
    const squareVal = square
    if (cardVal && squareVal) {
      const res = await cardVal.tokenize()

      if (res.status != "OK" || !res.token) {
        const errorMessage =
          res.errors && res.errors[0] ? res.errors[0].message : "Payment failed"
        throw new Error(errorMessage)
      }

      const verificationToken = await square.verifyBuyer(res.token)
      await squareVal.completeCheckout(
        res.token,
        idempotencyKey,
        verificationToken ?? undefined
      )
    }
  }

  useEffect(() => {
    loadSquare(checkoutData.sandbox !== false).then((square) => {
      setSquare(
        new SquareCheckout(
          square,
          checkoutData.application_id,
          checkoutData.location_id,
          state
        )
      )
    })
  }, [])

  useEffect(() => {
    if (square) {
      square.getCardPaymentMethod().then((card) => {
        setCard(card)
      })
    }
  }, [square])

  useEffect(() => {
    if (card && containerEl) {
      card.attach(containerEl).then(() => {
        if (!ready) {
          state.clearLoading()
        }

        setReady(true)
      })

      return () => {
        card.detach()
      }
    }
  }, [card, containerEl])

  return (
    <Box
      component="form"
      onSubmit={(e) => {
        e.preventDefault()
        if (submitting) {
          return
        }

        setSubmitting(true)
        state
          .wrapPromise(
            handleSubmit().catch((e) => {
              setSubmitting(false)
              throw e
            })
          )
          .catch(() => void 0)
          .finally(() => {
            setIdempotencyKey(makeKey(state.id))
          })
      }}
    >
      <Stack>
        <div ref={containerElRef}></div>
        <Button type="submit">Pay</Button>
      </Stack>
    </Box>
  )
}

// TODO: replace with a better ID function
const makeKey = (suffix: string) =>
  (Math.random().toString(36).substring(2) + suffix).substring(0, 45)
