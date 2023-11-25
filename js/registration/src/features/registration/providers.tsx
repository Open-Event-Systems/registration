import { RegistrationStoreContext } from "#src/features/registration/hooks"
import { RegistrationStore } from "#src/features/registration/stores/registration"
import { useWretch } from "#src/hooks/api"
import { ReactNode, useState } from "react"

export const RegistrationStoreProvider = ({
  children,
}: {
  children?: ReactNode
}) => {
  const wretch = useWretch()
  const [store] = useState(
    () => new RegistrationStore(wretch.url("/registrations")),
  )
  return (
    <RegistrationStoreContext.Provider value={store}>
      {children}
    </RegistrationStoreContext.Provider>
  )
}
