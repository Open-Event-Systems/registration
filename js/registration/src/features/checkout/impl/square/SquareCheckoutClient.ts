import { Checkout } from "#src/features/checkout/types/Checkout"
import { Card, Payments, Square } from "@square/web-payments-sdk-types"

declare module "#src/features/checkout/types/Checkout" {
  interface PaymentServiceMap {
    square: SquareCheckoutData
  }
}

export enum SquareCheckoutType {
  web = "web",
  terminal = "terminal",
}

export interface SquareCheckoutData {
  application_id: string
  location_id: string
  type?: SquareCheckoutType
  amount: string
  currency: string
  sandbox?: boolean
}

export interface SquareCheckoutUpdate {
  source_id: string
  idempotency_key: string
  verification_token?: string | null
}

export class SquareCheckoutClient {
  private payments: Payments

  constructor(
    square: Square,
    private applicationId: string,
    private locationId: string,
  ) {
    this.payments = square.payments(this.applicationId, this.locationId)
  }

  async getCardPaymentMethod(): Promise<Card> {
    return this.payments.card()
  }

  async verifyBuyer(
    checkout: Checkout<"square">,
    token: string,
  ): Promise<string | null> {
    const res = await this.payments.verifyBuyer(token, {
      amount: checkout.data.amount,
      intent: "CHARGE",
      currencyCode: checkout.data.currency,
      billingContact: {},
    })

    return res?.token ?? null
  }
}

export const loadSquare = (sandbox: boolean): Promise<Square> => {
  if (window.Square) {
    return Promise.resolve(window.Square)
  }

  const promise = new Promise<Square>((resolve) => {
    const el = document.createElement("script")

    el.addEventListener("load", () => {
      if (window.Square) {
        resolve(window.Square)
      }

      document.body.removeChild(el)
    })

    el.setAttribute(
      "src",
      sandbox
        ? "https://sandbox.web.squarecdn.com/v1/square.js"
        : "https://web.squarecdn.com/v1/square.js",
    )

    document.body.appendChild(el)
  })

  return promise
}
