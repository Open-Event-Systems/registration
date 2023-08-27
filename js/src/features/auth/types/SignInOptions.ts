import { AccountStore } from "#src/features/auth/stores/AccountStore.js"
import { ComponentType } from "react"

export type SignInOption = {
  id: string
  name: string
  description: string
  icon: ComponentType
}

export interface SignInOptions {
  [id: string]:
    | SignInOption
    | false
    | ((
        accountStore: AccountStore
      ) => Promise<SignInOption | false> | SignInOption | false)
  guest: SignInOption
  email: SignInOption
  webauthn: SignInOption
  platformWebAuthn: (
    accountStore: AccountStore
  ) => Promise<SignInOption> | SignInOption | false
}
