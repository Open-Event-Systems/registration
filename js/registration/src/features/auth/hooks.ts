import { placeholderWretch } from "#src/config/api.js"
import { AuthStore } from "#src/features/auth/stores/AuthStore.js"
import { createContext, useContext } from "react"

const defaultAuthStore = new AuthStore(
  new URL(window.location.href),
  placeholderWretch,
)

export const AuthContext = createContext(defaultAuthStore)

export const useAuth = () => useContext(AuthContext)
