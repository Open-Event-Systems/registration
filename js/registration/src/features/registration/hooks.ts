import { placeholderWretch } from "#src/config/api"
import { RegistrationAPI } from "#src/features/registration"
import { createRegistrationAPI } from "#src/features/registration/api"
import { createContext, useContext } from "react"

export const RegistrationAPIContext = createContext(
  createRegistrationAPI(placeholderWretch),
)

export const useRegistrationAPI = (): RegistrationAPI =>
  useContext(RegistrationAPIContext)
