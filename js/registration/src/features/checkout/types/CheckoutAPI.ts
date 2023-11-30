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
  list(options?: {
    registrationId?: string
    before?: string
  }): DefinedInitialDataOptions<CheckoutListResponse[]>
  create<ID extends string = string>(
    cartId: string,
  ): UseMutationOptions<
    Checkout<ID>,
    Error,
    { service: ID; method?: string | null }
  >
  read(checkoutId: string): UndefinedInitialDataOptions<Checkout>
  update(
    checkoutId: string,
  ): UseMutationOptions<
    Checkout | null,
    Error,
    Record<string, unknown> | undefined
  >
  cancel(checkoutId: string): UseMutationOptions<null>
}
