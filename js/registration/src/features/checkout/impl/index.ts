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
        "#src/features/checkout/impl/mock/MockCheckoutComponent"
      )
      Component = MockCheckoutComponent
      break
    case "system":
      const { SystemCheckoutComponent } = await import(
        "#src/features/checkout/impl/system/SystemCheckoutComponent"
      )
      Component = SystemCheckoutComponent
      break
    case "square":
      const { SquareCheckoutComponent } = await import(
        "#src/features/checkout/impl/square/SquareCheckoutComponent"
      )
      Component = SquareCheckoutComponent
      break
    default:
      throw new Error(`Unsupported payment service: ${service}`)
  }
  return Component as ComponentType<CheckoutRenderProps<T>>
}
