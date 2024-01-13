import { Config } from "#src/types/config"
import { defaultQueryClient, placeholderWretch } from "#src/config/api"
import { Wretch } from "wretch"
import { AuthStore } from "#src/features/auth/stores/AuthStore"
import { EventAPI } from "#src/features/event/types"
import { RegistrationAPI } from "#src/features/registration"
import { createEventAPI } from "#src/features/event/api"
import { createRegistrationAPI } from "#src/features/registration/api"
import { createContext } from "react"
import { CheckoutAPI } from "#src/features/checkout/types/CheckoutAPI"
import { createCheckoutAPI } from "#src/features/checkout/api"
import { SelfServiceAPI } from "#src/features/selfservice/types"
import { createSelfServiceAPI } from "#src/features/selfservice/api"
import { CartAPI } from "#src/features/cart/types"
import { createCartAPI } from "#src/features/cart/api"
import { QueryClient } from "@tanstack/react-query"
import { AuthAPI } from "#src/features/auth/types/api"
import { createAuthAPI } from "#src/features/auth/api"

import config from "#src/config/config"

export class AppStore {
  authStore: AuthStore
  authAPI: AuthAPI
  eventAPI: EventAPI
  cartAPI: CartAPI
  registrationAPI: RegistrationAPI
  checkoutAPI: CheckoutAPI
  selfServiceAPI: SelfServiceAPI

  constructor(
    public wretch: Wretch,
    public config: Config,
    public queryClient: QueryClient,
  ) {
    const apiUrl = new URL(config.apiUrl, window.location.href)
    this.authStore = new AuthStore(apiUrl, wretch)
    const authWretch = this.authStore.authWretch

    this.authAPI = createAuthAPI(wretch, authWretch, queryClient)
    this.eventAPI = createEventAPI(authWretch, queryClient)
    this.cartAPI = createCartAPI(authWretch, queryClient)
    this.registrationAPI = createRegistrationAPI(authWretch)
    this.checkoutAPI = createCheckoutAPI(authWretch, queryClient)
    this.selfServiceAPI = createSelfServiceAPI(authWretch, queryClient)
  }
}

export const AppContext = createContext(
  new AppStore(placeholderWretch, config, defaultQueryClient),
)

export const AppStoreContext = AppContext
