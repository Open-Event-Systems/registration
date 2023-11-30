import { defaultQueryClient, placeholderWretch } from "#src/config/api"
import { CheckoutState } from "#src/features/checkout/types/Checkout"
import {
  CheckoutListResponse,
  CheckoutResponse,
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
    create<ID extends string = string>(
      cartId: string,
    ): UseMutationOptions<
      Checkout<ID>,
      Error,
      { service: ID; method?: string | null }
    > {
      return {
        async mutationFn({ service, method = null }) {
          let req = cartWretch
            .url(`/${cartId}/checkout`)
            .addon(queryString)
            .query({ service: service })

          if (method) {
            req = req.query({ method: method })
          }

          const result = await req.post().json<CheckoutResponse<ID>>()
          return {
            cartId: cartId,
            data: result.data,
            externalId: result.external_id,
            id: result.id,
            method: method,
            service: service,
            state: result.state,
          }
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
          console.log("reading", checkoutId)
          const response = await checkoutWretch
            .url(`/${checkoutId}`)
            .get()
            .json<CheckoutResponse>()
          return {
            cartId: null,
            data: response.data,
            externalId: response.external_id,
            id: response.id,
            method: null,
            service: response.service,
            state: response.state,
          }
        },
        staleTime: Infinity,
      }
    },
    update(checkoutId) {
      return {
        async mutationFn(body = {}) {
          let req = checkoutWretch.url(`/${checkoutId}/update`)
          req = req.json(body)

          const response = await req.post().res()
          if (response.status == 204) {
            return null
          }

          const respData: CheckoutResponse = await response.json()
          return {
            cartId: null,
            data: respData.data,
            externalId: respData.external_id,
            id: respData.id,
            method: null,
            service: respData.service,
            state: respData.state,
          }
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
            client.setQueryData(
              this.read(checkoutId).queryKey,
              (old: Checkout | undefined): Checkout | undefined =>
                old
                  ? {
                      ...result,
                      cartId: old.cartId,
                      method: old.method,
                      state: CheckoutState.complete,
                    }
                  : result,
            )
          }
        },
      }
    },
    cancel(checkoutId) {
      return {
        mutationKey: ["checkouts", checkoutId, "cancel"],
        async mutationFn() {
          await checkoutWretch.url(`/${checkoutId}/cancel`).put().res()
          return null
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
