import { CheckoutRenderProps } from "#src/features/checkout/components/checkout/CheckoutComponent"
import { ComponentType } from "react"

/**
 * Get the checkout component for a service.
 */
export const getCheckoutComponent = async <T extends string = string>(
  service: T,
): Promise<ComponentType<CheckoutRenderProps<T>>> => {
  let Component: unknown
  switch (service) {
    case "mock":
      const { MockCheckoutComponent } = await import(
        "#src/features/checkout/impl/mock2/MockCheckoutComponent"
      )
      Component = MockCheckoutComponent
      break
    default:
      throw new Error(`Unsupported payment service: ${service}`)
  }
  return Component as ComponentType<CheckoutRenderProps<T>>
}
