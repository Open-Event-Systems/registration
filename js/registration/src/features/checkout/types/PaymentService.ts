import {
  PaymentServiceID,
  PaymentServiceMap,
} from "#src/features/checkout/types/Checkout"
import { CheckoutComponent } from "#src/features/checkout/types/CheckoutComponent"

export const checkoutComponents: {
  [K in keyof PaymentServiceMap]?: () => Promise<CheckoutComponent<K>>
} = {
  system: async () => {
    const module = await import(
      "#src/features/checkout/impl/mock/SystemCheckoutComponent"
    )
    return module.SystemCheckoutComponent
  },
  mock: async () => {
    const module = await import(
      "#src/features/checkout/impl/mock/MockCheckoutComponent"
    )
    return module.MockCheckoutComponent
  },
  stripe: async () => {
    const module = await import(
      "#src/features/checkout/impl/stripe/StripeCheckoutComponent"
    )
    return module.StripeCheckoutComponent
  },
  square: async () => {
    const module = await import(
      "#src/features/checkout/impl/square/SquareCheckoutComponent"
    )
    return module.SquareCheckoutComponent
  },
}

export const getCheckoutComponent = async <ID extends PaymentServiceID>(
  service: ID,
): Promise<CheckoutComponent<ID>> => {
  const promise = checkoutComponents[service]
  if (!promise) {
    throw new Error("Payment service unavailable")
  }
  const component = await promise()
  return component
}
