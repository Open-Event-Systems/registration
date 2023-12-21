import { useCheckout } from "#src/features/checkout/hooks"
import {
  SquareCheckoutClient,
  SquareCheckoutUpdate,
  loadSquare,
} from "#src/features/checkout/impl/square/SquareCheckoutClient"
import { Checkout } from "#src/features/checkout/types/Checkout"
import { Box, Button, Skeleton, Stack } from "@mantine/core"
import type { Card } from "@square/web-payments-sdk-types"
import { action, runInAction } from "mobx"
import { observer, useLocalObservable } from "mobx-react-lite"
import { FormEvent, useEffect } from "react"

export const SquareCardCheckoutComponent = observer(() => {
  const {
    id: checkoutId,
    checkout,
    update,
    error,
    setError,
    setSubmitting,
    updating,
  } = useCheckout()

  const localState = useLocalObservable(() => ({
    containerEl: null as HTMLDivElement | null,
    setContainerEl(el: HTMLDivElement | null) {
      this.containerEl = el
    },
    square: null as SquareCheckoutClient | null,
    card: null as Card | null,
    ready: false,
    idempotencyKey: makeKey(checkoutId),
  }))

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    if (updating) {
      return
    }

    const { square, card, idempotencyKey } = localState
    if (square && card && checkout) {
      setSubmitting(true)
      setError(null)
      try {
        let tokenRes
        let verificationToken

        try {
          tokenRes = await card.tokenize()
          if (tokenRes.status != "OK" || !tokenRes.token) {
            return
          }

          verificationToken = await square.verifyBuyer(
            checkout as Checkout<"square">,
            tokenRes.token,
          )
        } catch (e) {
          if (e instanceof Error) {
            setError(e.message)
          } else {
            setError(`${e}`)
          }
          throw e
        }

        const body = {
          source_id: tokenRes.token,
          idempotency_key: idempotencyKey,
          verification_token: verificationToken ?? undefined,
        } satisfies SquareCheckoutUpdate

        await update(body).catch(
          action(() => {
            localState.idempotencyKey = makeKey(checkoutId)
          }),
        )
      } finally {
        setSubmitting(false)
      }
    }
  }

  const checkoutData = (checkout as Checkout<"square"> | undefined)?.data

  useEffect(() => {
    if (checkoutData && !localState.square) {
      loadSquare(checkoutData.sandbox !== false)
        .then(
          action((square) => {
            const client = new SquareCheckoutClient(
              square,
              checkoutData.application_id,
              checkoutData.location_id,
            )
            localState.square = client
            return client
          }),
        )
        .then((client) => {
          return client.getCardPaymentMethod().then(
            action((card) => {
              localState.card = card
            }),
          )
        })
    }
  }, [checkoutData?.application_id, checkoutData?.location_id])

  useEffect(() => {
    const { card, containerEl } = localState
    if (card && containerEl) {
      card.attach(containerEl).then(
        action(() => {
          localState.ready = true
        }),
      )

      return () => {
        card.detach()
      }
    }
  }, [localState.card, localState.containerEl])

  return (
    <Box component="form" onSubmit={handleSubmit}>
      <Stack>
        {!localState.ready && <Placeholder />}
        <div ref={localState.setContainerEl}></div>
        <Button type="submit" variant="filled">
          Pay
        </Button>
      </Stack>
    </Box>
  )
})

SquareCardCheckoutComponent.displayName = "SquareCardCheckoutComponent"

const Placeholder = () => (
  <>
    <Skeleton h="5.5rem" />
    <Skeleton h="2.25rem" />
  </>
)

// TODO: replace with a better ID function
const makeKey = (suffix: string) =>
  (Math.random().toString(36).substring(2) + suffix).substring(0, 45)
