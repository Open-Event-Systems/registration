import {
  getSavedWebAuthnCredentialId,
  getWebAuthnAvailability,
} from "#src/features/auth/webauthn"
import { ComponentType } from "react"

export const signInOptions: Record<
  string,
  () => Promise<ComponentType | null>
> = {
  webAuthn: async () => {
    const support = await getWebAuthnAvailability()
    const credentialId = getSavedWebAuthnCredentialId()
    if (support && credentialId) {
      const { WebAuthnSignInOption } = await import(
        "#src/features/auth/options/WebAuthn"
      )
      return WebAuthnSignInOption
    } else {
      return null
    }
  },
  email: async () => {
    const { EmailSignInOption } = await import(
      "#src/features/auth/options/Email"
    )
    return EmailSignInOption
  },
  guest: async () => {
    const { GuestSignInOption } = await import(
      "#src/features/auth/options/Guest"
    )
    return GuestSignInOption
  },
  device: async () => {
    const loc = new URL(window.location.href)

    // hack: don't show device auth on self-service routes, unless in kiosk mode
    if (loc.pathname.startsWith("/events") && !loc.hash.includes("kiosk")) {
      return null
    }

    const { DeviceAuthOption } = await import(
      "#src/features/auth/options/Device"
    )
    return DeviceAuthOption
  },
}

export const signInComponents: Record<
  string,
  (() => Promise<ComponentType | null>) | undefined
> = {
  email: async () => {
    const { EmailSignIn } = await import("#src/features/auth/options/Email")
    return EmailSignIn
  },
  device: async () => {
    const { DeviceAuthComponent } = await import(
      "#src/features/auth/options/Device"
    )
    return DeviceAuthComponent
  },
}
