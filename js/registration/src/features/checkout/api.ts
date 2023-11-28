import { placeholderWretch } from "#src/config/api"
import {
  CheckoutListResponse,
  CheckoutResponse,
  PaymentServiceID,
} from "#src/features/checkout/types/Checkout"
import { CheckoutAPI } from "#src/features/checkout/types/CheckoutAPI"
import { createContext } from "react"
import { Wretch } from "wretch"
import queryString from "wretch/addons/queryString"

/**
 * Create a checkout for a cart.
 * @param wretch - The {@link Wretch} instance.
 * @param cartId - The cart Id.
 * @param service - The service ID.
 * @param method - The checkout method.
 * @returns The created checkout info.
 */
export const createCheckout = async <ID extends PaymentServiceID>(
  wretch: Wretch,
  cartId: string,
  service: ID,
  method: string | undefined,
): Promise<CheckoutResponse<ID>> => {
  const res = await wretch
    .url(`/carts/${cartId}/checkout`)
    .addon(queryString)
    .query({ service: service, method: method })
    .post()
    .json<CheckoutResponse<ID>>()

  return res
}

/**
 * Update a checkout.
 * @returns null if the checkout is complete, or additional checkout information if necessary.
 */
export const updateCheckout = async <ID extends PaymentServiceID>(
  wretch: Wretch,
  checkoutId: string,
  data?: Record<string, unknown>,
): Promise<CheckoutResponse<ID> | null> => {
  let req = await wretch.url(`/checkouts/${checkoutId}/update`)

  if (data) {
    req = req.json(data)
  }

  return await req
    .post()
    .error(422, (e) => {
      const errObj = e.json
      throw new Error(errObj.detail)
    })
    .res((res) => {
      if (res.status == 204) {
        return null
      }

      return res.json()
    })
}

/**
 * Cancel a checkout by ID.
 */
export const cancelCheckout = async (
  wretch: Wretch,
  checkoutId: string,
): Promise<void> => {
  await wretch.url(`/checkouts/${checkoutId}/cancel`).put().res()
}

export const createCheckoutAPI = (wretch: Wretch): CheckoutAPI => {
  const checkoutWretch = wretch.url("/checkouts")
  const cartWretch = wretch.url("/carts")
  return {
    list(options = {}) {
      let req = checkoutWretch.addon(queryString)

      if (options.registrationId) {
        req = req.query({ registration_id: options.registrationId })
      }

      if (options.before) {
        req = req.query({ before: options.before })
      }

      return {
        queryKey: ["checkouts", options],
        async queryFn() {
          return await req.get().json<CheckoutListResponse[]>()
        },
        initialData: [],
      }
    },
    async create<ID extends PaymentServiceID>(
      cartId: string,
      service: ID,
      method?: string,
    ) {
      return await cartWretch
        .url(`/${cartId}/checkout`)
        .addon(queryString)
        .query({ service: service, method: method })
        .post()
        .json<CheckoutResponse<ID>>()
    },
    async update(checkoutId: string, data?: Record<string, unknown>) {
      let req = await checkoutWretch.url(`/${checkoutId}/update`)

      if (data) {
        req = req.json(data)
      }

      return await req
        .post()
        .error(422, (e) => {
          const errObj = e.json
          throw new Error(errObj.detail)
        })
        .res((res) => {
          if (res.status == 204) {
            return null
          }

          return res.json()
        })
    },
    async cancel(checkoutId) {
      await checkoutWretch.url(`/${checkoutId}/cancel`).put().res()
    },
  }
}

export const CheckoutAPIContext = createContext(
  createCheckoutAPI(placeholderWretch),
)
