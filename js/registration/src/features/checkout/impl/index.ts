import { CheckoutImplComponentType } from "#src/features/checkout/types/Checkout"

/**
 * Get the checkout component for a service.
 */
export const getCheckoutImplComponentType = async <T extends string = string>(
  service: T,
): Promise<CheckoutImplComponentType> => {
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
    case "suspend":
      const { SuspendCheckoutComponent } = await import(
        "#src/features/checkout/impl/suspend/SuspendCheckoutComponent"
      )
      Component = SuspendCheckoutComponent
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
  return Component as CheckoutImplComponentType
}
