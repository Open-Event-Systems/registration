import { CartAPIContext } from "#src/features/cart/api"
import { CartAPI } from "#src/features/cart/types"
import { useContext } from "react"

export const useCartAPI = (): CartAPI => useContext(CartAPIContext)
