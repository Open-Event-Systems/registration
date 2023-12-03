import { useCheckoutMethods } from "#src/features/cart/hooks"
import { useCreateCheckout } from "#src/features/checkout/hooks"
import { CheckoutMethod } from "#src/features/checkout/types/Checkout"
import { useLocation, useNavigate } from "#src/hooks/location"
import { Button, Skeleton, Stack } from "@mantine/core"
import { useLayoutEffect, useState } from "react"

export type CheckoutMethodsProps = {
  methods?: CheckoutMethod[]
  onSelect?: (method: string) => void
}

export const CheckoutMethods = (props: CheckoutMethodsProps) => {
  const { methods, onSelect } = props

  const buttonEls = methods?.map((m) => (
    <Button
      key={m.method}
      onClick={() => {
        onSelect && onSelect(m.method)
      }}
      size="md"
      variant="subtle"
    >
      {m.name}
    </Button>
  ))

  return <Button.Group orientation="vertical">{buttonEls}</Button.Group>
}

CheckoutMethods.Placeholder = () => (
  <Stack>
    <Skeleton h="2.25rem" />
    <Skeleton h="2.25rem" />
  </Stack>
)

/**
 * Display the {@link CheckoutMethods} for the current cart.
 * @returns D
 */
CheckoutMethods.Manager = ({ cartId }: { cartId: string }) => {
  const loc = useLocation()
  const navigate = useNavigate()

  const methods = useCheckoutMethods(cartId)
  const create = useCreateCheckout(cartId)

  const [creating, setCreating] = useState(false)

  const onSelect = async (method: string) => {
    setCreating(true)
    try {
      const checkout = await create(method)
      navigate(loc, {
        state: {
          showCheckoutDialog: {
            ...loc.state?.showCheckoutDialog,
            checkoutId: checkout.id,
          },
        },
        replace: true,
      })
    } finally {
      setCreating(false)
    }
  }

  useLayoutEffect(() => {
    // auto select the only option
    if (methods.isSuccess && methods.data.length == 1) {
      onSelect(methods.data[0].method)
    }
  }, [methods.isSuccess, methods.data])

  if (!methods.isSuccess || creating || methods.data.length == 1) {
    return <CheckoutMethods.Placeholder />
  }

  return <CheckoutMethods methods={methods.data} onSelect={onSelect} />
}
