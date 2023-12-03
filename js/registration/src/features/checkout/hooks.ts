import { CheckoutAPIContext } from "#src/features/checkout/api"
import { CheckoutContext } from "#src/features/checkout/providers"
import {
  Checkout,
  CheckoutContextValue,
} from "#src/features/checkout/types/Checkout"
import { CheckoutAPI } from "#src/features/checkout/types/CheckoutAPI"
import { useLocation, useNavigate } from "#src/hooks/location"
import { useMutation } from "@tanstack/react-query"
import { useCallback, useContext } from "react"

/**
 * Get a function to create a checkout.
 * @param cartId - the cart ID
 */
export const useCreateCheckout = (
  cartId: string,
): ((method: string) => Promise<Checkout>) => {
  const api = useCheckoutAPI()
  const mutation = useMutation(api.create(cartId))
  const func = useCallback(
    async (method: string) => {
      return await mutation.mutateAsync({ method: method })
    },
    [mutation.mutate],
  )

  return func
}

/**
 * Return a function to show the checkout dialog.
 */
export const useShowCheckout = (): ((cartId: string) => void) => {
  const loc = useLocation()
  const navigate = useNavigate()

  const func = useCallback(
    (cartId: string) => {
      navigate(loc, {
        state: { ...loc.state, showCheckoutDialog: { cartId: cartId } },
      })
    },
    [navigate],
  )
  return func
}

export const useCheckout = (): CheckoutContextValue => {
  const value = useContext(CheckoutContext)
  if (!value) {
    throw new Error("No checkout context provided")
  }
  return value
}

export const useCheckoutAPI = (): CheckoutAPI => useContext(CheckoutAPIContext)
