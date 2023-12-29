import { ComponentType } from "react"

// eslint-disable-next-line @typescript-eslint/no-empty-interface
export interface PaymentServiceMap {}

export type PaymentServiceID = keyof PaymentServiceMap

export enum CheckoutState {
  pending = "pending",
  canceled = "canceled",
  complete = "complete",
}

export interface CheckoutMethod {
  name: string
  method: string
}

export type CheckoutExternalData<ID extends string = string> =
  ID extends PaymentServiceID ? PaymentServiceMap[ID] : Record<string, unknown>

declare module "#src/hooks/location" {
  interface LocationState {
    showCheckoutDialog?: {
      cartId?: string
      checkoutId?: string
      service?: PaymentServiceID
      eventId?: string
    }
  }
}

export interface CheckoutListResponse {
  id: string
  service: string
  state: CheckoutState
  date: string
  event_id?: string
  first_name?: string
  last_name?: string
  email?: string
  url?: string
  cart_id?: string
  receipt_id?: string
  receipt_url?: string
}

export type Checkout<ID extends string = string> = {
  /**
   * The checkout ID on the server.
   */
  id: string

  /**
   * The service ID.
   */
  service: ID

  /**
   * The checkout ID in the external service.
   */
  externalId: string

  /**
   * The checkout state.
   */
  state: CheckoutState

  /**
   * The data associated with the checkout.
   */
  data: CheckoutExternalData<ID>
}

export type CheckoutContextValue = {
  id: string
  ready: boolean
  checkout?: Checkout
  error: string | null
  setError: (error: string | null | undefined) => void
  setSubmitting: (submitting: boolean) => void
  updating: boolean
  update: (body?: Record<string, unknown>) => Promise<Checkout | null>
  cancel: () => Promise<void>
} & (
  | { ready: true; checkout: Checkout }
  | { ready: false; checkout?: Checkout }
)

export type CheckoutImplComponentType = ComponentType<Record<string, never>>
