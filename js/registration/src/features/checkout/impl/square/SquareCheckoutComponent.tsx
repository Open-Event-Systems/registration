import { CheckoutImplComponentProps } from "#src/features/checkout/components/checkout/CheckoutComponent"
import {
  SquareCheckoutClient,
  SquareCheckoutUpdate,
  loadSquare,
} from "#src/features/checkout/impl/square/SquareCheckoutClient"
import { Box, Button, Stack } from "@mantine/core"
import type { Card } from "@square/web-payments-sdk-types"
import { action } from "mobx"
import { observer, useLocalObservable } from "mobx-react-lite"
import { FormEvent, useEffect } from "react"

export const SquareCheckoutComponent = observer(
  (props: CheckoutImplComponentProps<"square">) => {
    const {
      checkoutId,
      checkout,
      setError,
      isSubmitting,
      setSubmitting,
      update,
    } = props

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
      if (isSubmitting) {
        return
      }

      const { square, card, idempotencyKey } = localState
      if (square && card && checkout) {
        setSubmitting(true)
        setError(null)
        try {
          const tokenRes = await card.tokenize()
          if (tokenRes.status != "OK" || !tokenRes.token) {
            const errorMessage =
              tokenRes.errors && tokenRes.errors[0]
                ? tokenRes.errors[0].message
                : "Payment failed"
            setError(errorMessage)
            return
          }

          const verificationToken = await square.verifyBuyer(
            checkout,
            tokenRes.token,
          )
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
        } catch (e) {
          setError(`${e}`)
        } finally {
          setSubmitting(false)
        }
      }
    }

    const checkoutData = checkout?.data

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
          <div ref={localState.setContainerEl}></div>
          <Button type="submit" variant="filled">
            Pay
          </Button>
        </Stack>
      </Box>
    )
  },
)

SquareCheckoutComponent.displayName = "SquareCheckoutComponent"

// TODO: replace with a better ID function
const makeKey = (suffix: string) =>
  (Math.random().toString(36).substring(2) + suffix).substring(0, 45)
