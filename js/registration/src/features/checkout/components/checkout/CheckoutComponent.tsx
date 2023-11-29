import { useCheckoutAPI } from "#src/features/checkout/hooks"
import { getCheckoutComponent } from "#src/features/checkout/impl"
import { Checkout } from "#src/features/checkout/types/Checkout"
import { useMutation, useQuery } from "@tanstack/react-query"
import { ComponentType, ReactNode, useEffect, useState } from "react"

export type CheckoutImplComponentProps<T extends string = string> = {
  isSubmitting: boolean
  checkout?: Checkout<T>
  error?: string
  update: (body?: Record<string, unknown>) => void
  cancel: () => void
}

export type CheckoutRenderProps<T extends string = string> = {
  Component?: ComponentType<CheckoutImplComponentProps<T>>
} & CheckoutImplComponentProps<T>

export type CheckoutComponentProps = {
  checkoutId: string
  children: (renderProps: CheckoutRenderProps) => ReactNode
}

/**
 * Displays the checkout.
 */
export const CheckoutComponent = (props: CheckoutComponentProps) => {
  const { checkoutId, children } = props

  const checkoutAPI = useCheckoutAPI()
  const checkoutQuery = useQuery(checkoutAPI.read(checkoutId))
  const update = useMutation(checkoutAPI.update(checkoutId))
  const cancel = useMutation(checkoutAPI.cancel(checkoutId))
  const [Component, setComponent] =
    useState<ComponentType<CheckoutRenderProps> | null>(null)

  useEffect(() => {
    setComponent(null)
    const service = checkoutQuery.data?.service

    if (service) {
      getCheckoutComponent(service).then((res) => {
        if (checkoutQuery.data?.service == service) {
          setComponent(() => res)
        }
      })
    }
  }, [checkoutQuery.data?.service])

  return children({
    Component: Component ?? undefined,
    isSubmitting: update.isPending,
    checkout: checkoutQuery.data,
    error: update.error?.message,
    update(body) {
      update.mutate(body)
    },
    cancel() {
      cancel.mutate()
    },
  })
}
