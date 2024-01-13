import {
  Checkout,
  CheckoutListResponse,
} from "#src/features/checkout/types/Checkout"
import {
  DefinedInitialDataOptions,
  UndefinedInitialDataOptions,
  UseMutationOptions,
} from "@tanstack/react-query"

export type CheckoutAPI = {
  list(
    query?: string,
    options?: {
      registrationId?: string
      before?: string
      showAll?: boolean
    },
  ): DefinedInitialDataOptions<CheckoutListResponse[]>
  create(
    cartId: string,
  ): UseMutationOptions<Checkout, Error, { method: string }>
  read(checkoutId: string): UndefinedInitialDataOptions<Checkout>
  update(
    checkoutId: string,
  ): UseMutationOptions<
    Checkout | null,
    Error,
    Record<string, unknown> | undefined
  >
  cancel(checkoutId: string): UseMutationOptions<void>
}
