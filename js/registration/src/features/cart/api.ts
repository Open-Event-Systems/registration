import { Wretch } from "wretch"
import { queryStringAddon } from "wretch/addons"
import { Cart, CartAPI, PricingResult } from "#src/features/cart/types"
import { CheckoutMethod } from "#src/features/checkout/types/Checkout"
import { StateResponse } from "@open-event-systems/interview-lib"
import { createContext } from "react"
import { defaultQueryClient, placeholderWretch } from "#src/config/api"
import { getCurrentCartId, setCurrentCartId } from "#src/features/cart/utils"
import { QueryClient } from "@tanstack/react-query"

/**
 * Fetch the empty cart for an event.
 */
export const fetchEmptyCart = async (
  wretch: Wretch,
  eventId: string,
): Promise<[string, Cart]> => {
  const res = await wretch
    .url("/carts/empty")
    .addon(queryStringAddon)
    .query({ event_id: eventId })
    .get()
    .res()

  const body: Cart = await res.json()

  const url = new URL(res.url)
  const pathParts = url.pathname.split("/")
  const id = pathParts[pathParts.length - 1]

  return [id, body]
}

/**
 * Fetch a cart by ID.
 */
export const fetchCart = async (
  wretch: Wretch,
  cartId: string,
): Promise<Cart> => {
  const res = await wretch.url(`/carts/${cartId}`).get().json<Cart>()

  return res
}

/**
 * Fetch the pricing result for a cart.
 */
export const fetchCartPricingResult = async (
  wretch: Wretch,
  cartId: string,
) => {
  const res = await wretch
    .url(`/carts/${cartId}/pricing-result`)
    .get()
    .json<PricingResult>()
  return res
}

/**
 * Fetch a new interview state for a cart.
 */
export const fetchCartInterview = async (
  wretch: Wretch,
  cartId: string,
  interviewId: string,
  registrationId?: string,
  accessCode?: string,
): Promise<StateResponse> => {
  let req = wretch.url(`/carts/${cartId}/new-interview`).addon(queryStringAddon)

  if (interviewId) {
    req = req.query({
      interview_id: interviewId,
    })
  }

  if (registrationId) {
    req = req.query({
      registration_id: registrationId,
    })
  }

  if (accessCode) {
    req = req.query({
      access_code: accessCode,
    })
  }

  return await req.get().json<StateResponse>()
}

/**
 * Fetch the available checkout methods for a cart.
 */
export const fetchAvailableCheckoutMethods = async (
  wretch: Wretch,
  cartId: string,
): Promise<CheckoutMethod[]> => {
  const res = await wretch
    .url(`/carts/${cartId}/checkout-methods`)
    .get()
    .json<CheckoutMethod[]>()
  return res
}

/**
 * Remove a registration from a cart.
 * @param wretch - The {@link Wretch} instance.
 * @param cartId - The cart ID.
 * @param registrationId - The registration ID.
 * @returns A pair of the new cart ID and the cart object.
 */
export const removeRegistrationFromCart = async (
  wretch: Wretch,
  cartId: string,
  registrationId: string,
): Promise<[string, Cart]> => {
  const res = await wretch
    .url(`/carts/${cartId}/registrations/${registrationId}`)
    .delete()
    .res()

  const body: Cart = await res.json()

  const url = new URL(res.url)
  const pathParts = url.pathname.split("/")
  const id = pathParts[pathParts.length - 1]
  return [id, body]
}

export const createCartAPI = (wretch: Wretch, client: QueryClient): CartAPI => {
  wretch = wretch.url("/carts")

  return {
    readEmptyCart(eventId) {
      return {
        queryKey: ["carts", { eventId: eventId }],
        async queryFn() {
          const res = await wretch
            .url("/empty")
            .addon(queryStringAddon)
            .query({ event_id: eventId })
            .get()
            .res()
          const id = getCartIdFromResponse(res)
          const body: Cart = await res.json()
          return [id, body]
        },
        staleTime: 300000,
      }
    },
    readCart(id) {
      return {
        queryKey: ["carts", id],
        async queryFn() {
          const res = await wretch.url(`/${id}`).get().res()
          const body: Cart = await res.json()
          return [id, body]
        },
        staleTime: 300000,
      }
    },
    readPricingResult(id) {
      return {
        queryKey: ["carts", id, "pricing-result"],
        async queryFn() {
          return await wretch
            .url(`/${id}/pricing-result`)
            .get()
            .json<PricingResult>()
        },
        staleTime: 300000,
      }
    },
    readAddInterview(cartId, interviewId, options = {}) {
      return {
        queryKey: ["carts", cartId, { interviewId: interviewId, ...options }],
        async queryFn() {
          let req = wretch
            .url(`/${cartId}/new-interview`)
            .addon(queryStringAddon)
            .query({ interview_id: interviewId })

          if (options.registrationId) {
            req = req.query({ registration_id: options.registrationId })
          }

          if (options.accessCode) {
            req = req.query({ access_code: options.accessCode })
          }

          return await req.get().json<StateResponse>()
        },
      }
    },
    readCheckoutMethods(id) {
      return {
        queryKey: ["carts", id, "checkout-methods"],
        async queryFn() {
          return await wretch
            .url(`/${id}/checkout-methods`)
            .get()
            .json<CheckoutMethod[]>()
        },
        staleTime: 300000,
      }
    },
    removeRegistrationFromCart(cartId) {
      return {
        async mutationFn(registrationId) {
          const res = await wretch
            .url(`/${cartId}/registrations/${registrationId}`)
            .delete()
            .res()
          const newCartId = getCartIdFromResponse(res)
          const body: Cart = await res.json()
          return [newCartId, body]
        },
        onSuccess([newCartId, newCart]) {
          client.setQueryData(["carts", newCartId], [newCartId, newCart])
        },
      }
    },
    readCurrentCart(eventId) {
      return {
        queryKey: ["carts", { current: true, eventId: eventId }],
        queryFn: async () => {
          const currentCartId = getCurrentCartId(eventId)
          if (currentCartId) {
            return await client.ensureQueryData(this.readCart(currentCartId))
          } else {
            return null
          }
        },
        placeholderData(prev) {
          return prev
        },
      }
    },
    setCurrentCart(eventId) {
      return {
        mutationFn([cartId, cart]) {
          setCurrentCartId(eventId, cartId)
          return Promise.resolve([cartId, cart])
        },
        onSuccess([cartId, cart]) {
          client.setQueryData(
            ["carts", { current: true, eventId: eventId }],
            [cartId, cart],
          )
        },
      }
    },
  }
}

export const getCartIdFromResponse = (cartResponse: Response): string => {
  const url = new URL(cartResponse.url)
  const pathParts = url.pathname.split("/")
  return pathParts[pathParts.length - 1]
}

export const CartAPIContext = createContext(
  createCartAPI(placeholderWretch, defaultQueryClient),
)
