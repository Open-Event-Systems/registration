// eslint-disable-next-line @typescript-eslint/no-empty-interface
export interface PaymentServiceMap {}

export type PaymentServiceID = keyof PaymentServiceMap

export enum CheckoutState {
  pending = "pending",
  canceled = "canceled",
  complete = "complete",
}

export interface CheckoutMethod {
  service: string
  method?: string
  name?: string
}

export type CheckoutExternalData<ID extends string = string> =
  ID extends PaymentServiceID ? PaymentServiceMap[ID] : Record<string, unknown>

declare module "#src/hooks/location" {
  interface LocationState {
    showCheckoutDialog?: {
      cartId: string
      checkoutId: string
      service: PaymentServiceID
      method?: string
    }
  }
}

export interface CheckoutListResponse {
  id: string
  service: string
  state: CheckoutState
  date: string
  url?: string
}

export interface CheckoutResponse<ID extends string = string> {
  id: string
  service: ID
  external_id: string
  state: CheckoutState
  data: CheckoutExternalData<ID>
}

export type Checkout<ID extends string = string> = {
  /**
   * The cart ID.
   */
  cartId: string | null

  /**
   * The service ID.
   */
  service: ID

  /**
   * The payment method
   */
  method: string | null

  /**
   * The checkout ID on the server.
   */
  id: string

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

// export type Checkout<ID extends string = string> = {
//   /**
//    * The cart ID.
//    */
//   get cartId(): string

//   /**
//    * The service ID.
//    */
//   get service(): ID

//   /**
//    * The payment method
//    */
//   get method(): string | null

//   /**
//    * The checkout ID on the server.
//    */
//   get id(): string

//   /**
//    * The checkout ID in the external service.
//    */
//   get externalId(): string

//   /**
//    * The checkout state.
//    */
//   get state(): CheckoutState

//   /**
//    * The data associated with the checkout.
//    */
//   get data(): CheckoutExternalData<ID>

//   /**
//    * The current error.
//    */
//   get error(): string | null

//   /**
//    * Update the checkout.
//    */
//   update(body?: Record<string, unknown>): Promise<CheckoutResponse<ID> | null>

//   /**
//    * Cancel the checkout.
//    */
//   cancel(): Promise<void>
// }
