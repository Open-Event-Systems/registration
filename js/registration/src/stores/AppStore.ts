import { Config } from "#src/types/config"
import { defaultWretch, placeholderWretch } from "#src/config/api"
import { Wretch } from "wretch"
import { fetchConfig } from "#src/config/config"
import { AuthStore } from "#src/features/auth/stores/AuthStore"
import { EventAPI } from "#src/features/event/types"
import { RegistrationAPI } from "#src/features/registration"
import { createEventAPI } from "#src/features/event/api"
import { createRegistrationAPI } from "#src/features/registration/api"
import { createContext } from "react"
import { CheckoutAPI } from "#src/features/checkout/types/CheckoutAPI"
import { createCheckoutAPI } from "#src/features/checkout/api"

export class AppStore {
  authStore: AuthStore
  eventAPI: EventAPI
  registrationAPI: RegistrationAPI
  checkoutAPI: CheckoutAPI

  constructor(
    public wretch: Wretch,
    public config: Config,
  ) {
    const apiUrl = new URL(config.apiUrl, window.location.href)
    this.authStore = new AuthStore(apiUrl, wretch)
    const authWretch = this.authStore.authWretch

    this.eventAPI = createEventAPI(authWretch)
    this.registrationAPI = createRegistrationAPI(authWretch)
    this.checkoutAPI = createCheckoutAPI(authWretch)
  }

  static async fromConfig(): Promise<AppStore> {
    const config = await fetchConfig()
    const wretch = defaultWretch.url(config.apiUrl, true)
    return new AppStore(wretch, config)
  }
}

const defaultConfig: Config = {
  apiUrl: "http://localhost:8000",
}

export const AppContext = createContext(
  new AppStore(placeholderWretch, defaultConfig),
)
export const AppStoreContext = AppContext
