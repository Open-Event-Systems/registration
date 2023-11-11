import {
  RegistrationAPIContext,
  createRegistrationAPI,
} from "#src/features/registration/api"
import { useWretch } from "#src/hooks/api"
import { ReactNode, useState } from "react"

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
