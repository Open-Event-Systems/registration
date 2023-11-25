// eslint-disable-next-line @typescript-eslint/no-empty-interface
export interface PaymentServiceMap {
  // empty
}

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

export interface CheckoutExternalData {
  [key: string]: unknown
}

export interface CheckoutListResponse {
  id: string
  service: PaymentServiceID
  state: CheckoutState
  date: string
  url?: string
}

export interface CheckoutResponse<ID extends PaymentServiceID> {
  id: string
  service: ID
  external_id: string
  data: PaymentServiceMap[ID]
}
