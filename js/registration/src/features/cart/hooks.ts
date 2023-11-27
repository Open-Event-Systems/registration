import { placeholderWretch } from "#src/config/api"
import { CartAPIContext } from "#src/features/cart/api"
import { CartStore, CurrentCartStore } from "#src/features/cart/stores"
import { CartAPI } from "#src/features/cart/types"
import { makeInterviewRecordStore } from "@open-event-systems/interview-lib"
import { createContext, useContext } from "react"

const defaultStore = new CartStore(
  placeholderWretch,
  makeInterviewRecordStore(),
)

export const CartStoreContext = createContext(defaultStore)
export const CurrentCartStoreContext = createContext(
  new CurrentCartStore(placeholderWretch, "", defaultStore),
)

export const useCartStore = () => useContext(CartStoreContext)
export const useCurrentCartStore = () => useContext(CurrentCartStoreContext)

export const useCartAPI = (): CartAPI => useContext(CartAPIContext)
