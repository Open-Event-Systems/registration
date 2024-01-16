import { CheckoutImplComponent } from "#src/features/checkout/components/checkout/CheckoutImplComponent"
import { CheckoutDialog } from "#src/features/checkout/components/dialog/CheckoutDialog"
import { CheckoutMethods } from "#src/features/checkout/components/methods/CheckoutMethods"
import { useCheckout, useCheckoutAPI } from "#src/features/checkout/hooks"
import { CheckoutProvider } from "#src/features/checkout/providers"
import { Checkout, CheckoutState } from "#src/features/checkout/types/Checkout"
import { useLocation, useNavigate } from "#src/hooks/location"
import { LoadingOverlay, Text } from "@mantine/core"
import { useQueryClient } from "@tanstack/react-query"
import { ReactNode, useEffect, useLayoutEffect, useState } from "react"

/**
 * Manage the checkout dialog and the checkout state.
 */
export const CheckoutManager = ({
  onComplete,
}: {
  onComplete?: (checkout: Checkout) => void
}) => {
  const loc = useLocation()
  const navigate = useNavigate()

  const client = useQueryClient()
  const checkoutAPI = useCheckoutAPI()
  const [prevIds, setPrevIds] = useState<
    [string | undefined, string | undefined]
  >([undefined, undefined])

  const curCartId = loc.state?.showCheckoutDialog?.cartId
  const curCheckoutId = loc.state?.showCheckoutDialog?.checkoutId

  const cartId = curCartId || prevIds[0]
  const checkoutId = curCheckoutId || prevIds[1]

  useLayoutEffect(() => {
    if (cartId && checkoutId) {
      setPrevIds([cartId, checkoutId])
    }
  }, [cartId, checkoutId])

  const show = !!curCartId || !!curCheckoutId

  let content
  if (checkoutId) {
    content = (
      <CheckoutProvider key={checkoutId} checkoutId={checkoutId}>
        <CheckoutManagerCheckout />
      </CheckoutProvider>
    )
  } else if (cartId) {
    content = <CheckoutMethods.Manager key={cartId} cartId={cartId} />
  }

  return (
    <CheckoutDialog
      opened={show}
      onClose={() => {
        navigate(-1)
      }}
      transitionProps={{
        onExit() {
          if (checkoutId) {
            const checkout = client.getQueryData<Checkout>(
              checkoutAPI.read(checkoutId).queryKey,
            )
            if (checkout?.state == CheckoutState.complete && onComplete) {
              onComplete(checkout)
            }
          }
        },
        onExited() {
          setPrevIds([undefined, undefined])
        },
      }}
    >
      {content}
    </CheckoutDialog>
  )
}

const CheckoutManagerCheckout = () => {
  const { id, checkout, cancel, error, updating, completeMessage } =
    useCheckout()
  const checkoutAPI = useCheckoutAPI()
  const client = useQueryClient()

  useEffect(() => {
    return () => {
      // cancel on unmount
      const cur = client.getQueryData<Checkout>(checkoutAPI.read(id).queryKey)

      if (cur?.state == CheckoutState.pending) {
        cancel()
      }
    }
  }, [id])

  let content
  switch (checkout?.state) {
    case CheckoutState.canceled:
      content = <CheckoutManager.Canceled />
      break
    case CheckoutState.complete:
      content = <CheckoutManager.Complete message={completeMessage} />
      break
    default:
      content = (
        <CheckoutImplComponent fallback={<CheckoutManager.Placeholder />} />
      )
      break
  }

  return (
    <>
      {content}
      {error && <Text c="red">{error}</Text>}
      <LoadingOverlay visible={updating} />
    </>
  )
}

CheckoutManager.Complete = ({ message }: { message?: ReactNode }) =>
  message ? message : <Text component="p">Your order is complete.</Text>

CheckoutManager.Canceled = () => (
  <Text component="p">This checkout has been canceled.</Text>
)

CheckoutManager.Placeholder = CheckoutMethods.Placeholder
