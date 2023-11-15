import { Loader, createLoader } from "#src/features/loader"
import { Registration } from "#src/features/registration"
import { createContext, useContext } from "react"

export const RegistrationContext = createContext<Loader<Registration>>(
  createLoader(() => Promise.reject()),
)

export const useRegistration = (): Loader<Registration> =>
  useContext(RegistrationContext)
