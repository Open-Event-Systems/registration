import { useCheckout } from "#src/features/checkout/hooks"
import { getCheckoutImplComponentType } from "#src/features/checkout/impl"
import { CheckoutImplComponentType } from "#src/features/checkout/types/Checkout"
import { ReactNode, useEffect, useState } from "react"

export type CheckoutComponentProps = {
  fallback?: ReactNode
}

/**
 * Loads and renders a checkout implementation's component.
 */
export const CheckoutImplComponent = ({ fallback }: CheckoutComponentProps) => {
  const { ready, checkout } = useCheckout()

  const [Component, setComponent] = useState<CheckoutImplComponentType | null>(
    () => null,
  )

  useEffect(() => {
    const service = checkout?.service
    setComponent(null)
    if (service) {
      getCheckoutImplComponentType(service).then((c) => {
        setComponent(() => c)
      })
    }
  }, [checkout?.service])

  if (!ready || !Component) {
    return fallback
  }

  return <Component />
}
