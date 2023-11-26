import { AuthContext } from "#src/features/auth/hooks"
import { CheckoutAPIContext } from "#src/features/checkout/api"
import { EventAPIContext } from "#src/features/event/hooks"
import { RegistrationAPIContext } from "#src/features/registration/hooks"
import { WretchContext } from "#src/hooks/api"
import { AppContext, AppStore } from "#src/stores/AppStore"
import { Context, ReactNode, useLayoutEffect, useState } from "react"

export const AppProvider = ({
  children,
  fallback,
}: {
  children?: ReactNode
  fallback?: ReactNode
}) => {
  const [app, setApp] = useState<AppStore | null>(null)

  useLayoutEffect(() => {
    AppStore.fromConfig()
      .then((app) => {
        return app.authStore.load().then(() => app)
      })
      .then((app) => setApp(app))
  }, [])

  if (!app) {
    return fallback
  }

  return (
    <ContextProvider
      contexts={[
        AppContext,
        AuthContext,
        WretchContext,
        EventAPIContext,
        RegistrationAPIContext,
        CheckoutAPIContext,
      ]}
      values={[
        app,
        app.authStore,
        app.authStore.authWretch,
        app.eventAPI,
        app.registrationAPI,
        app.checkoutAPI,
      ]}
    >
      {children}
    </ContextProvider>
  )
}

type ContextProviderProps<V extends [unknown, ...unknown[]]> = {
  values: V
  contexts: { [K in keyof V]: Context<V[K]> }
  children?: ReactNode
}

const ContextProvider = <V extends [unknown, ...unknown[]]>(
  props: ContextProviderProps<V>,
) => {
  const { contexts, values, children } = props
  let content = children

  for (let i = contexts.length - 1; i >= 0; i--) {
    const context = contexts[i]
    const value = values[i]
    content = <context.Provider value={value}>{content}</context.Provider>
  }

  return content
}
