import { useCheckout } from "#src/features/checkout/hooks"
import { SquareCardCheckoutComponent } from "#src/features/checkout/impl/square/Card"
import { SquareCheckoutType } from "#src/features/checkout/impl/square/SquareCheckoutClient"
import { SquareTerminalCheckoutComponent } from "#src/features/checkout/impl/square/Terminal"
import { Checkout } from "#src/features/checkout/types/Checkout"

export const SquareCheckoutComponent = () => {
  const { checkout } = useCheckout()

  const squareCheckout = checkout as Checkout<"square">

  if (squareCheckout.data.type == SquareCheckoutType.terminal) {
    return <SquareTerminalCheckoutComponent />
  } else {
    return <SquareCardCheckoutComponent />
  }
}
