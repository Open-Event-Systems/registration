import { AuthInfo } from "#src/features/auth/stores/AuthInfo.js"
import { ComponentType, ReactNode } from "react"
import { Wretch } from "wretch"

export interface SignInState {
  readonly webAuthnError: boolean
  setWebAuthnError(): void
}

export type SignInOptionComponentProps = {
  onComplete: (authInfo: AuthInfo) => void
  loading: boolean
  setLoading: (loading: boolean) => void
}

/**
 * A sign in option.
 */
export interface SignInOption {
  readonly id: string
  readonly name: string
  readonly description: string | null
  readonly icon: ComponentType | null
  readonly highlight?: boolean

  getRender(): Promise<
    ((props: SignInOptionComponentProps) => ReactNode) | AuthInfo | null
  >
}

export type SignInOptionFactory = (
  wretch: Wretch,
  state: SignInState,
) => Promise<SignInOption | null>

export interface SignInOptions {
  [id: string]: SignInOptionFactory
}
