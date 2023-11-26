import {
  CheckoutListResponse,
  CheckoutResponse,
  PaymentServiceID,
} from "#src/features/checkout/types/Checkout"
import { DefinedInitialDataOptions } from "@tanstack/react-query"

export type CheckoutAPI = {
  list(options?: {
    registrationId?: string
    before?: string
  }): DefinedInitialDataOptions<CheckoutListResponse[]>
  create<ID extends PaymentServiceID>(
    cartId: string,
    service: ID,
    method?: string,
  ): Promise<CheckoutResponse<ID>>
  update<ID extends PaymentServiceID>(
    checkoutId: string,
    data?: Record<string, unknown>,
  ): Promise<CheckoutResponse<ID> | null>
  cancel(checkoutId: string): Promise<void>
}
