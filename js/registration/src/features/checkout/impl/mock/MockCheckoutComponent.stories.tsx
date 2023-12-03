import { defaultQueryClient, placeholderWretch } from "#src/config/api"
import { CartAPIContext, createCartAPI } from "#src/features/cart/api"
import { CartAPI } from "#src/features/cart/types"
import {
  CheckoutAPIContext,
  createCheckoutAPI,
} from "#src/features/checkout/api"
import { CheckoutManager } from "#src/features/checkout/components/checkout/CheckoutManager"
import { useShowCheckout } from "#src/features/checkout/hooks"
import { MockCheckoutComponent } from "#src/features/checkout/impl/mock/MockCheckoutComponent"
import { CheckoutState } from "#src/features/checkout/types/Checkout"
import { CheckoutAPI } from "#src/features/checkout/types/CheckoutAPI"
import { useLocation, useNavigate } from "#src/hooks/location"
import { Button } from "@mantine/core"
import { Meta, StoryObj } from "@storybook/react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { useState } from "react"
import { RouterProvider, createMemoryRouter } from "react-router-dom"

const meta: Meta<typeof MockCheckoutComponent> = {
  component: MockCheckoutComponent,
}

export default meta

export const Default: StoryObj<typeof MockCheckoutComponent> = {
  decorators: [
    (Story) => {
      const router = createMemoryRouter([
        {
          path: "*",
          element: <Story />,
        },
      ])

      return <RouterProvider router={router} />
    },
  ],
  render() {
    const [cartId, setCartId] = useState(1)
    const cartAPI = createMockCartAPI(defaultQueryClient)
    const checkoutAPI = createMockCheckoutAPI(defaultQueryClient)
    const showCheckout = useShowCheckout()
    const loc = useLocation()
    const navigate = useNavigate()

    const cartIdStr = `${cartId}`

    return (
      <QueryClientProvider client={defaultQueryClient}>
        <CartAPIContext.Provider value={cartAPI}>
          <CheckoutAPIContext.Provider value={checkoutAPI}>
            <Button
              onClick={() => {
                showCheckout(cartIdStr)
              }}
            >
              Checkout
            </Button>
            <CheckoutManager
              onComplete={() => {
                navigate(loc, {
                  state: { showCheckoutDialog: undefined },
                  replace: true,
                })
                setCartId(cartId + 1)
              }}
            />
          </CheckoutAPIContext.Provider>
        </CartAPIContext.Provider>
      </QueryClientProvider>
    )
  },
}

const createMockCartAPI = (client: QueryClient): CartAPI => {
  const cartAPI = createCartAPI(placeholderWretch, client)
  return {
    ...cartAPI,
    readCheckoutMethods(cartId) {
      return {
        ...cartAPI.readCheckoutMethods(cartId),
        async queryFn() {
          await wait()
          return [{ method: "mock", name: "Mock" }]
        },
      }
    },
  }
}

const createMockCheckoutAPI = (client: QueryClient): CheckoutAPI => {
  const checkoutAPI = createCheckoutAPI(placeholderWretch, client)
  const [checkoutId, setCheckoutId] = useState(1)
  return {
    ...checkoutAPI,
    create(cartId) {
      return {
        ...checkoutAPI.create(cartId),
        async mutationFn() {
          await wait()
          setCheckoutId(checkoutId + 1)
          return {
            id: `${checkoutId}`,
            externalId: `mock-${checkoutId}`,
            data: {},
            service: "mock",
            state: CheckoutState.pending,
          }
        },
      }
    },
    update(checkoutId) {
      return {
        ...checkoutAPI.update(checkoutId),
        async mutationFn(body = {}) {
          await wait()
          const card = body.card

          if (!card || typeof card != "string" || !/[0-9]+/.test(card)) {
            throw new Error("Invalid card")
          }

          return null
        },
      }
    },
    cancel(checkoutId) {
      return {
        ...checkoutAPI.cancel(checkoutId),
        async mutationFn() {
          await wait()
        },
      }
    },
  }
}

const wait = () => new Promise((r) => window.setTimeout(r, 1000))
