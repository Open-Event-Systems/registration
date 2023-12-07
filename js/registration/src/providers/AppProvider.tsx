import { AuthAPIContext } from "#src/features/auth/api"
import { AuthContext } from "#src/features/auth/hooks"
import { CartAPIContext } from "#src/features/cart/api"
import { CheckoutAPIContext } from "#src/features/checkout/api"
import { EventAPIContext } from "#src/features/event/hooks"
import { RegistrationAPIContext } from "#src/features/registration/hooks"
import { SelfServiceAPIContext } from "#src/features/selfservice/api"
import { WretchContext } from "#src/hooks/api"
import { AppContext, AppStore } from "#src/stores/AppStore"
import { QueryClient } from "@tanstack/react-query"
import { Context, ReactNode, useLayoutEffect, useState } from "react"

export const AppProvider = ({
  children,
  queryClient,
  fallback,
}: {
  children?: ReactNode
  queryClient: QueryClient
  fallback?: ReactNode
}) => {
  const [app, setApp] = useState<AppStore | null>(null)

  useLayoutEffect(() => {
    AppStore.fromConfig(queryClient)
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
        AuthAPIContext,
        EventAPIContext,
        CartAPIContext,
        RegistrationAPIContext,
        CheckoutAPIContext,
        SelfServiceAPIContext,
      ]}
      values={[
        app,
        app.authStore,
        app.authStore.authWretch,
        app.authAPI,
        app.eventAPI,
        app.cartAPI,
        app.registrationAPI,
        app.checkoutAPI,
        app.selfServiceAPI,
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
