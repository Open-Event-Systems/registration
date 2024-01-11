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

import config from "#src/config/config"
import { defaultWretch } from "#src/config/api"
import { QueueAPIContext } from "#src/features/queue/hooks"

export const AppProvider = ({
  children,
  queryClient,
}: {
  children?: ReactNode
  queryClient: QueryClient
  fallback?: ReactNode
}) => {
  const [wretch] = useState(defaultWretch.url(config.apiUrl))
  const [app] = useState(new AppStore(wretch, config, queryClient))

  useLayoutEffect(() => {
    app.authStore.load()
  }, [app])

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
        QueueAPIContext,
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
        app.queueAPI,
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
