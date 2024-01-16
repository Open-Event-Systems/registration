import {
  CheckInStore,
  CheckInStoreContext,
} from "#src/features/checkin/stores/CheckInStore"
import { useContext } from "react"

export const useCheckInStore = (): CheckInStore =>
  useContext(CheckInStoreContext)
