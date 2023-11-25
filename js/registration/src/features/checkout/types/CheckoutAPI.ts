import {
  CheckoutListResponse,
  CheckoutResponse,
  PaymentServiceID,
} from "#src/features/checkout/types/Checkout"
import { PaginatedResult } from "#src/types/api"

export type CheckoutAPI = {
  list(
    registrationId?: string,
  ): Promise<PaginatedResult<CheckoutListResponse[]>>
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
