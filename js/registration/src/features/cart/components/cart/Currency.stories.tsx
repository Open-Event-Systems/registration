import {
  Currency,
  CurrencyContext,
  CurrencyProps,
} from "#src/features/cart/components/cart/Currency"
import { Meta, StoryFn } from "@storybook/react"

const meta: Meta<CurrencyProps & { currency: string }> = {
  component: Currency,
  args: {
    amount: 1000,
    currency: "USD",
  },
}

export default meta

export const Default: StoryFn<CurrencyProps & { currency: string }> = (
  args,
) => {
  return (
    <CurrencyContext.Provider value={args.currency}>
      <Currency amount={args.amount} />
    </CurrencyContext.Provider>
  )
}
