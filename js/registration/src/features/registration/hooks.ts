import { placeholderWretch } from "#src/config/api"
import { RegistrationStore } from "#src/features/registration/stores/registration"
import { createContext, useContext } from "react"

export const RegistrationStoreContext = createContext(
  new RegistrationStore(placeholderWretch),
)
export const useRegistrationStore = (): RegistrationStore =>
  useContext(RegistrationStoreContext)
