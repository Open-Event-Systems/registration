import { getDeviceAuthSignIn } from "#src/features/auth/components/signin/DeviceAuth"
import { getEmailSignIn } from "#src/features/auth/components/signin/EmailAuth"
import { getGuestSignIn } from "#src/features/auth/components/signin/Guest"
import {
  getPlatformWebAuthnSignIn,
  getWebAuthnAuthenticationSignIn,
} from "#src/features/auth/components/signin/WebAuthn"
import { SignInOptions } from "#src/features/auth/types/SignInOptions"

export const signInOptions: SignInOptions = {
  webAuthnAuthentication: getWebAuthnAuthenticationSignIn,
  email: getEmailSignIn,
  platformWebAuthn: getPlatformWebAuthnSignIn,
  guest: getGuestSignIn,
  device: getDeviceAuthSignIn,
}
