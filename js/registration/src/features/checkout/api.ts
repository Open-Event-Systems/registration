import { defaultQueryClient, placeholderWretch } from "#src/config/api"
import { CheckoutState } from "#src/features/checkout/types/Checkout"
import {
  CheckoutListResponse,
  Checkout,
} from "#src/features/checkout/types/Checkout"
import { CheckoutAPI } from "#src/features/checkout/types/CheckoutAPI"
import { QueryClient, UseMutationOptions } from "@tanstack/react-query"
import { createContext } from "react"
import { Wretch } from "wretch"
import queryString from "wretch/addons/queryString"

export const createCheckoutAPI = (
  wretch: Wretch,
  client: QueryClient,
): CheckoutAPI => {
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
    create(
      cartId: string,
    ): UseMutationOptions<Checkout, Error, { method: string }> {
      return {
        async mutationFn({ method }) {
          let req = cartWretch
            .url(`/${cartId}/checkout`)
            .addon(queryString)
            .query({ method: method })
          return await req.post().json<Checkout>()
        },
        onSuccess: (response) => {
          client.setQueryData(this.read(response.id).queryKey, response)
        },
      }
    },
    read(checkoutId) {
      return {
        queryKey: ["checkouts", checkoutId],
        async queryFn() {
          return await checkoutWretch
            .url(`/${checkoutId}`)
            .get()
            .json<Checkout>()
        },
        staleTime: Infinity,
      }
    },
    update(checkoutId) {
      return {
        mutationKey: ["checkouts", checkoutId],
        async mutationFn(body = {}) {
          let req = checkoutWretch.url(`/${checkoutId}/update`)
          req = req.json(body)

          const response = await req.post().res()
          if (response.status == 204) {
            return null
          }

          return await response.json()
        },
        onSuccess: (result) => {
          if (result == null) {
            // completed
            client.setQueryData(
              this.read(checkoutId).queryKey,
              (old: Checkout | undefined): Checkout | undefined =>
                old ? { ...old, state: CheckoutState.complete } : undefined,
            )
          } else {
            client.setQueryData(this.read(checkoutId).queryKey, result)
          }
        },
      }
    },
    cancel(checkoutId) {
      return {
        mutationKey: ["checkouts", checkoutId, "cancel"],
        async mutationFn() {
          await checkoutWretch.url(`/${checkoutId}/cancel`).put().res()
        },
        onSuccess: () => {
          client.setQueryData(
            this.read(checkoutId).queryKey,
            (old: Checkout | undefined): Checkout | undefined =>
              old ? { ...old, state: CheckoutState.canceled } : undefined,
          )
        },
      }
    },
  }
}

export const CheckoutAPIContext = createContext(
  createCheckoutAPI(placeholderWretch, defaultQueryClient),
)
