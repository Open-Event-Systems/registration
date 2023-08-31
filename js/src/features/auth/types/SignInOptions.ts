import { AuthInfo } from "#src/features/auth/stores/AuthInfo.js"
import { WebAuthnChallenge } from "#src/features/auth/types/WebAuthn.js"
import { ComponentType } from "react"
import { Wretch } from "wretch"

export type SignInOption = {
  id: string
  name: string
  description?: string
  icon: ComponentType
  factory: SignInMethodFactory
}

export interface SignInOptions {
  [id: string]:
    | SignInOption
    | false
    | ((
        signInState: SignInState
      ) => Promise<SignInOption | false> | SignInOption | false)
  guest: SignInOption
  email: SignInOption
  webAuthn: SignInOption | (() => false)
  platformWebAuthn: (
    signInState: SignInState
  ) => Promise<SignInOption | false> | SignInOption
}

export interface SignInState {
  readonly wretch: Wretch

  readonly isWebAuthnAvailable: "platform" | boolean

  readonly webAuthnRegistrationChallenge: WebAuthnChallenge | null
  webAuthnCredentialId: string | null
  webAuthnError: boolean

  loading: boolean

  handleComplete(authInfo: AuthInfo): void
}

export type SignInComponentProps = {
  state: SignInState
}

export type SignInMethodFactory = (
  state: SignInState
) => Promise<ComponentType<SignInComponentProps> | null>
