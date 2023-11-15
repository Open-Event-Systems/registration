import { NotFoundError, createLoader } from "#src/features/loader"
import {
  RegistrationAPIContext,
  createRegistrationAPI,
  useRegistrationAPI,
} from "#src/features/registration/api"
import { RegistrationContext } from "#src/features/registration/hooks"
import { useWretch } from "#src/hooks/api"
import { ReactNode, useCallback, useMemo, useState } from "react"

export const RegistrationAPIProvider = ({
  children,
}: {
  children?: ReactNode
}) => {
  const wretch = useWretch()
  const [api] = useState(() => createRegistrationAPI(wretch))
  return (
    <RegistrationAPIContext.Provider value={api}>
      {children}
    </RegistrationAPIContext.Provider>
  )
}

export const RegistrationProvider = ({
  id,
  children,
}: {
  id: string
  children?: ReactNode
}) => {
  const api = useRegistrationAPI()
  const loadFunc = useCallback(async () => {
    const reg = await api.read(id)
    if (!reg) {
      throw new NotFoundError()
    }
    return reg
  }, [id])

  const loader = useMemo(() => createLoader(loadFunc), [loadFunc])

  return (
    <RegistrationContext.Provider key={id} value={loader}>
      {children}
    </RegistrationContext.Provider>
  )
}
