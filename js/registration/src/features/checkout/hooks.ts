import { CheckoutAPIContext } from "#src/features/checkout/api"
import { CheckoutAPI } from "#src/features/checkout/types/CheckoutAPI"
import { useContext } from "react"

export const useCheckoutAPI = (): CheckoutAPI => useContext(CheckoutAPIContext)
