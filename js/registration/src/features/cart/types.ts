import { CheckoutMethod } from "#src/features/checkout/types/Checkout"
import { StateResponse } from "@open-event-systems/interview-lib"
import {
  UndefinedInitialDataOptions,
  UseMutationOptions,
} from "@tanstack/react-query"

export interface CartRegistration {
  id: string
  submission_id?: string
  old_data: Record<string, unknown>
  new_data: Record<string, unknown>
  meta?: Record<string, unknown>
}

// TODO: this will not always have data
export interface Cart {
  event_id: string
  registrations: CartRegistration[]
  meta?: Record<string, unknown>
}

export interface Modifier {
  name: string
  amount: number
}

export interface LineItem {
  registration_id: string
  name: string
  price: number
  total_price: number
  modifiers: Modifier[]
  description?: string
}

export interface PricingResultRegistration {
  registration_id: string
  line_items: LineItem[]
  name?: string | null
}

export interface PricingResult {
  receipt_url?: string
  date?: string
  currency: string
  registrations: PricingResultRegistration[]
  total_price: number
  modifiers: Modifier[]
}

export interface InterviewOption {
  id: string
  name: string
}

export type CartAPI = {
  readEmptyCart(eventId: string): UndefinedInitialDataOptions<[string, Cart]>
  readCart(id: string): UndefinedInitialDataOptions<[string, Cart]>
  readPricingResult(id: string): UndefinedInitialDataOptions<PricingResult>
  readAddInterview(
    cartId: string,
    interviewId: string,
    options?: { registrationId?: string; accessCode?: string },
  ): UndefinedInitialDataOptions<StateResponse>
  readCheckoutMethods(
    cartId: string,
  ): UndefinedInitialDataOptions<CheckoutMethod[]>
  removeRegistrationFromCart(
    cartId: string,
  ): UseMutationOptions<[string, Cart], Error, string>
  readCurrentCart(
    eventId: string,
  ): UndefinedInitialDataOptions<[string, Cart] | null>
  setCurrentCart(
    eventId: string,
  ): UseMutationOptions<[string, Cart], Error, [string, Cart]>
}

declare module "@open-event-systems/interview-lib" {
  interface InterviewStateMetadata {
    eventId?: string
    cartId?: string
  }
}

declare module "#src/hooks/location" {
  interface LocationState {
    showInterviewDialog?: {
      eventId?: string
      recordId: string
    }
  }
}
