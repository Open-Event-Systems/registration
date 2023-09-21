import { createAccount } from "#src/features/auth/api.js"
import { getWebAuthnAvailability } from "#src/features/auth/components/signin/WebAuthn.js"
import { AuthInfo } from "#src/features/auth/stores/AuthInfo.js"
import {
  SignInOption,
  SignInState,
} from "#src/features/auth/types/SignInOptions.js"
import { IconUserOff } from "@tabler/icons-react"
import { Wretch } from "wretch"

/**
 * Perform guest sign-in.
 */
class GuestSignIn implements SignInOption {
  id = "guest"
  name = "Continue as guest"
  description = "You might not be able to make changes later"
  icon = IconUserOff

  constructor(private wretch: Wretch) {}

  async getRender() {
    const result = await createAccount(this.wretch)
    const authInfo = AuthInfo.createFromResponse(result)
    return authInfo
  }
}

/**
 * Get a guest sign in state.
 */
export const getGuestSignIn = async (wretch: Wretch, state: SignInState) => {
  const webAuthnAvailable = await getWebAuthnAvailability()

  if (webAuthnAvailable == "platform" && !state.webAuthnError) {
    // prefer webauthn
    return null
  }

  return new GuestSignIn(wretch)
}
