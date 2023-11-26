import { placeholderWretch } from "#src/config/api"
import { RegistrationAPI } from "#src/features/registration"
import { createRegistrationAPI } from "#src/features/registration/api"
import { RegistrationStore } from "#src/features/registration/stores/registration"
import { createContext, useContext } from "react"

export const RegistrationAPIContext = createContext(
  createRegistrationAPI(placeholderWretch),
)

export const RegistrationStoreContext = createContext(
  new RegistrationStore(placeholderWretch),
)
export const useRegistrationStore = (): RegistrationStore =>
  useContext(RegistrationStoreContext)

export const useRegistrationAPI = (): RegistrationAPI =>
  useContext(RegistrationAPIContext)
