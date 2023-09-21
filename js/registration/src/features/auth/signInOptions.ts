import { getEmailSignIn } from "#src/features/auth/components/signin/EmailAuth.js"
import { getGuestSignIn } from "#src/features/auth/components/signin/Guest.js"
import {
  getPlatformWebAuthnSignIn,
  getWebAuthnAuthenticationSignIn,
} from "#src/features/auth/components/signin/WebAuthn.js"
import { SignInOptions } from "#src/features/auth/types/SignInOptions.js"

export const signInOptions: SignInOptions = {
  webAuthnAuthentication: getWebAuthnAuthenticationSignIn,
  email: getEmailSignIn,
  platformWebAuthn: getPlatformWebAuthnSignIn,
  guest: getGuestSignIn,
}
