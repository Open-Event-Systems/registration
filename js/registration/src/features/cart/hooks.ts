import { CartAPIContext } from "#src/features/cart/api"
import { CartAPI } from "#src/features/cart/types"
import { CheckoutMethod } from "#src/features/checkout/types/Checkout"
import { UseQueryResult, useQuery } from "@tanstack/react-query"
import { useContext } from "react"

/**
 * Get a query for the checkout methods available for a cart.
 */
export const useCheckoutMethods = (
  cartId: string,
): UseQueryResult<CheckoutMethod[]> => {
  const api = useCartAPI()
  const query = useQuery(api.readCheckoutMethods(cartId))

  return query
}

export const useCartAPI = (): CartAPI => useContext(CartAPIContext)
