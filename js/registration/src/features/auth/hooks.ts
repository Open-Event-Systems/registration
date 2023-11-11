import { placeholderWretch } from "#src/config/api"
import { AuthStore } from "#src/features/auth/stores/AuthStore"
import { createContext, useContext } from "react"

const defaultAuthStore = new AuthStore(
  new URL(window.location.href),
  placeholderWretch,
)

export const AuthContext = createContext(defaultAuthStore)

export const useAuth = () => useContext(AuthContext)
