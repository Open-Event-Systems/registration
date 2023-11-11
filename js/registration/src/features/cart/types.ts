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
