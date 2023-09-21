import { placeholderWretch } from "#src/config/api.js"
import {
  checkAccessCode,
  listSelfServiceRegistrations,
} from "#src/features/selfservice/api.js"
import { createLoader } from "#src/util/loader.js"
import { createContext, useContext } from "react"

export const SelfServiceLoaderContext = createContext(
  createLoader(() => listSelfServiceRegistrations(placeholderWretch))
)

export const useSelfServiceLoader = () => useContext(SelfServiceLoaderContext)

export const AccessCodeLoaderContext = createContext(
  createLoader(() => checkAccessCode(placeholderWretch, "", ""))
)

export const useAccessCodeLoader = () => useContext(AccessCodeLoaderContext)
