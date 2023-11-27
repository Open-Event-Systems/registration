import { placeholderWretch } from "#src/config/api"
import {
  SelfServiceAPIContext,
  checkAccessCode,
  listSelfServiceRegistrations,
} from "#src/features/selfservice/api"
import { SelfServiceAPI } from "#src/features/selfservice/types"
import { createLoader } from "#src/util/loader"
import { createContext, useContext } from "react"

export const SelfServiceLoaderContext = createContext(
  createLoader(() => listSelfServiceRegistrations(placeholderWretch)),
)

export const useSelfServiceLoader = () => useContext(SelfServiceLoaderContext)

export const AccessCodeLoaderContext = createContext(
  createLoader(() => checkAccessCode(placeholderWretch, "", "")),
)

export const useAccessCodeLoader = () => useContext(AccessCodeLoaderContext)

export const useSelfServiceAPI = (): SelfServiceAPI =>
  useContext(SelfServiceAPIContext)
