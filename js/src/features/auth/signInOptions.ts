import { SignInOptions } from "#src/features/auth/types/SignInOptions.js"
import { PlatformWebAuthnDetails } from "#src/features/auth/types/WebAuthn.js"
import {
  IconAt,
  IconBrandWindows,
  IconFingerprint,
  IconKey,
  IconUser,
} from "@tabler/icons-react"

export const signInOptions: SignInOptions = {
  email: {
    id: "email",
    name: "Sign in with email",
    description: "Use your email address to sign in",
    icon: IconAt,
  },
  platformWebAuthn(accountStore) {
    // TODO: refactor to wait for check to complete, check failure count, etc.
    if (!accountStore.webAuthnAvailable) {
      return false
    }

    const details = getPlatformWebAuthnDetails(window.navigator.userAgent)

    return {
      id: "platformWebAuthn",
      name: details.name,
      description: details.description,
      icon: details.icon,
    }
  },
  webauthn: {
    id: "webauthn",
    name: "Use security key",
    description: "Use a security key to sign in",
    icon: IconKey,
  },
  guest: {
    id: "guest",
    name: "Continue as guest",
    description: "You might not be able to make changes later",
    icon: IconUser,
  },
}

/**
 * Get names/descriptions/icons for different platforms' WebAuthn implementation.
 */
export const getPlatformWebAuthnDetails = (
  userAgent: string
): PlatformWebAuthnDetails => {
  if (/(iPhone|iPad)/.test(userAgent)) {
    return {
      name: "Use Touch ID",
      description: "Sign in using Touch ID",
      emailName: "Continue with Touch ID",
      emailDescription: "Stay signed in using Touch ID",
      emailSkip: "Don't stay signed in",
      icon: IconFingerprint,
    }
  } else if (/android/i.test(userAgent)) {
    return {
      name: "Use device",
      description: "Sign in with your phone's keyring/Touch ID",
      emailName: "Rememberme",
      emailDescription: "Stay signed in using your phone's keyring/Touch ID",
      emailSkip: "Don't stay signed in",
      icon: IconFingerprint,
    }
  } else if (/(win32|win64|windows)/i.test(userAgent)) {
    return {
      name: "Sign in with Windows",
      description: "Use your PIN or security key",
      emailName: "Remember me",
      emailDescription: "Use your Windows account to stay signed in",
      emailSkip: "Don't stay signed in",
      icon: IconBrandWindows,
    }
  } else {
    return {
      name: "Use your passkey",
      description: "Sign in with a PIN, fingerprint, or security key",
      emailName: "Stay signed in with passkey",
      emailDescription: "Use your PIN, fingerprint, or security key",
      emailSkip: "Don't stay signed in",
      icon: IconKey,
    }
  }
}
