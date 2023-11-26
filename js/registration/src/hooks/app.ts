import { AppStore, AppStoreContext } from "#src/stores/AppStore"
import { useContext } from "react"

export const useApp = (): AppStore => useContext(AppStoreContext)
export const useAppStore = useApp
