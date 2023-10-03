import { CheckoutState } from "#src/features/checkout/CheckoutState.js"
import { Card, Payments, Square } from "@square/web-payments-sdk-types"

declare module "#src/features/checkout/types/Checkout.js" {
  interface PaymentServiceMap {
    square: SquareCheckoutData
  }
}

export interface SquareCheckoutData {
  application_id: string
  location_id: string
  amount: string
  currency: string
  sandbox?: boolean
}

export interface SquareCheckoutUpdate {
  source_id: string
  idempotency_key: string
  verification_token?: string | null
}

export class SquareCheckout {
  private payments: Payments

  constructor(
    square: Square,
    private applicationId: string,
    private locationId: string,
    private checkoutState: CheckoutState<"square">,
  ) {
    this.payments = square.payments(this.applicationId, this.locationId)
  }

  async getCardPaymentMethod(): Promise<Card> {
    return this.payments.card()
  }

  async verifyBuyer(token: string): Promise<string | null> {
    const res = await this.payments.verifyBuyer(token, {
      amount: this.checkoutState.data.amount,
      intent: "CHARGE",
      currencyCode: this.checkoutState.data.currency,
      billingContact: {},
    })

    return res?.token ?? null
  }

  async completeCheckout(
    token: string,
    idempotencyKey: string,
    verificationToken?: string,
  ) {
    const update: Record<string, unknown> & SquareCheckoutUpdate = {
      source_id: token,
      idempotency_key: idempotencyKey,
      verification_token: verificationToken,
    }

    await this.checkoutState.update(update)
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
