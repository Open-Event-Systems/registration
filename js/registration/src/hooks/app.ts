import { placeholderWretch } from "#src/config/api"
import { AppStore } from "#src/stores/AppStore"
import { Config } from "#src/types/config"
import { createContext, useContext } from "react"

const defaultConfig: Config = {
  apiUrl: "http://localhost:8000",
}

export const AppStoreContext = createContext(
  new AppStore(placeholderWretch, defaultConfig),
)

export const useAppStore = () => useContext(AppStoreContext)
