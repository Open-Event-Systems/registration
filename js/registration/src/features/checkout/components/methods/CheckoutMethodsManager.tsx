import { useCartAPI } from "#src/features/cart/hooks"
import { CheckoutMethodsDialog } from "#src/features/checkout/components/methods/CheckoutMethodsDialog"
import { useCheckoutAPI } from "#src/features/checkout/hooks"
import { PaymentServiceID } from "#src/features/checkout/types/Checkout"
import { useLocation, useNavigate } from "#src/hooks/location"
import { useMutation, useQuery } from "@tanstack/react-query"

declare module "#src/hooks/location" {
  interface LocationState {
    showCheckoutMethodsDialog?: string
  }
}

export type CheckoutMethodsManagerProps = {
  cartId: string
}

export const CheckoutMethodsManager = ({
  cartId,
}: CheckoutMethodsManagerProps) => {
  const cartAPI = useCartAPI()
  const checkoutAPI = useCheckoutAPI()
  const loc = useLocation()
  const navigate = useNavigate()

  const opened = loc.state?.showCheckoutMethodsDialog == cartId

  const methods = useQuery({ ...cartAPI.readCheckoutMethods(cartId) })
  const createCheckout = useMutation(checkoutAPI.create(cartId))

  return (
    <CheckoutMethodsDialog
      opened={opened}
      onClose={() => navigate(-1)}
      methods={methods.data}
      loading={!methods.isSuccess}
      onSelect={(service, method) => {
        navigate(loc, {
          state: { showCheckoutMethodsDialog: undefined },
          replace: true,
        })
        createCheckout.mutate(
          { service: service, method: method },
          {
            onSuccess(checkout) {
              navigate(loc, {
                state: {
                  showCheckoutDialog: {
                    checkoutId: checkout.id,
                    cartId: cartId,
                    service: service as PaymentServiceID,
                    method: method,
                  },
                },
                replace: true,
              })
            },
          },
        )
      }}
    />
  )
}
