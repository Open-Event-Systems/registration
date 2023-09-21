import {
  completeWebAuthnAuthentication,
  completeWebAuthnRegistration,
  getWebAuthnAuthenticationChallenge,
  getWebAuthnRegistrationChallenge,
} from "#src/features/auth/api.js"
import { AuthInfo } from "#src/features/auth/stores/AuthInfo.js"
import {
  SignInOption,
  SignInState,
} from "#src/features/auth/types/SignInOptions.js"
import {
  PlatformWebAuthnDetails,
  WebAuthnChallenge,
} from "#src/features/auth/types/WebAuthn.js"
import {
  browserSupportsWebAuthn,
  platformAuthenticatorIsAvailable,
  startAuthentication,
  startRegistration,
} from "@simplewebauthn/browser"
import { IconBrandWindows, IconFingerprint, IconKey } from "@tabler/icons-react"
import { makeAutoObservable } from "mobx"
import { Wretch } from "wretch"

/**
 * The local storage key for the stored credential ID.
 */
const WEBAUTHN_CREDENTIAL_ID_LOCAL_STORAGE_KEY = "oes-credential-id-v1"

class PlatformWebAuthnOption implements SignInOption {
  id = "platformWebAuthn"

  challenge: WebAuthnChallenge
  onError: (() => void) | null = null

  get webAuthnDetails() {
    return getPlatformWebAuthnDetails(window.navigator.userAgent)
  }

  get name() {
    return this.webAuthnDetails.name
  }

  get description() {
    return this.webAuthnDetails.description
  }

  get icon() {
    return this.webAuthnDetails.icon
  }

  constructor(
    public wretch: Wretch,
    challenge: WebAuthnChallenge,
    onError?: () => void
  ) {
    this.challenge = challenge
    this.onError = onError ?? null
    makeAutoObservable(this)
  }

  async getRender() {
    const result = await performWebAuthnRegistration(
      this.wretch,
      this.challenge
    )
    if (result) {
      const [credentialId, tokenResponse] = result
      saveWebAuthnCredentialId(credentialId)
      return tokenResponse
    } else {
      this.onError && this.onError()
      return null
    }
  }
}

/**
 * Get platform WebAuthn sign in.
 */
export const getPlatformWebAuthnSignIn = async (
  wretch: Wretch,
  state: SignInState
) => {
  const credentialId = getSavedWebAuthnCredentialId()

  // this is for registration only, not auth
  if (credentialId) {
    return null
  }

  const webAuthnAvailable = await getWebAuthnAvailability()

  if (webAuthnAvailable == "platform") {
    const challenge = await getWebAuthnRegistrationChallenge(wretch)
    return new PlatformWebAuthnOption(wretch, challenge, () =>
      state.setWebAuthnError()
    )
  } else {
    return null
  }
}

class WebAuthnAuthenticationOption implements SignInOption {
  id = "webAuthnAuthentication"
  highlight = true

  challenge: WebAuthnChallenge
  onError: (() => void) | null = null

  get webAuthnDetails() {
    return getPlatformWebAuthnDetails(window.navigator.userAgent)
  }

  get name() {
    return this.webAuthnDetails.name
  }

  get description() {
    return this.webAuthnDetails.description
  }

  get icon() {
    return this.webAuthnDetails.icon
  }

  constructor(
    public wretch: Wretch,
    challenge: WebAuthnChallenge,
    onError?: () => void
  ) {
    this.challenge = challenge
    this.onError = onError ?? null
    makeAutoObservable(this)
  }

  async getRender() {
    const result = await performWebAuthnAuthentication(
      this.wretch,
      this.challenge
    )
    if (result) {
      return result
    } else {
      this.onError && this.onError()
      return null
    }
  }
}

/**
 * Get WebAuthn authentication sign in.
 */
export const getWebAuthnAuthenticationSignIn = async (wretch: Wretch) => {
  const credentialId = getSavedWebAuthnCredentialId()

  // must have a saved credential
  if (!credentialId) {
    return null
  }

  const webAuthnAvailable = await getWebAuthnAvailability()

  if (webAuthnAvailable) {
    const challenge = await getWebAuthnAuthenticationChallenge(
      wretch,
      credentialId
    )
    return new WebAuthnAuthenticationOption(wretch, challenge)
  } else {
    return null
  }
}

/**
 * Get whether WebAuthn is available.
 */
export const getWebAuthnAvailability = async (): Promise<
  "platform" | boolean
> => {
  let available: "platform" | boolean = false
  if (browserSupportsWebAuthn()) {
    if (await platformAuthenticatorIsAvailable()) {
      available = "platform"
    } else {
      available = true
    }
  }
  return available
}

export const performWebAuthnRegistration = async (
  wretch: Wretch,
  challenge: WebAuthnChallenge,
  emailToken?: string | null
): Promise<[string, AuthInfo] | null> => {
  let registration
  try {
    registration = await startRegistration(challenge.options)
  } catch (err) {
    console.error("WebAuthn registration failed", err)
    return null
  }

  if (!registration) {
    console.error("WebAuthn registration failed")
    return null
  }

  const result = await completeWebAuthnRegistration(wretch, {
    challenge: challenge.challenge,
    result: JSON.stringify(registration),
    email_token: emailToken,
  })

  if (result) {
    return [registration.id, AuthInfo.createFromResponse(result)]
  } else {
    return null
  }
}

export const performWebAuthnAuthentication = async (
  wretch: Wretch,
  challenge: WebAuthnChallenge
): Promise<AuthInfo | null> => {
  let auth
  try {
    auth = await startAuthentication(challenge.options)
  } catch (err) {
    console.error("WebAuthn authentication failed", err)
    return null
  }

  if (!auth) {
    console.error("WebAuthn authentication failed")
    return null
  }

  const result = await completeWebAuthnAuthentication(wretch, {
    challenge: challenge.challenge,
    result: JSON.stringify(auth),
  })

  if (result) {
    return AuthInfo.createFromResponse(result)
  } else {
    return null
  }
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
      emailName: "Remember me",
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

/**
 * Get the saved WebAuthn credential ID.
 */
export const getSavedWebAuthnCredentialId = () => {
  const id = window.localStorage.getItem(
    WEBAUTHN_CREDENTIAL_ID_LOCAL_STORAGE_KEY
  )
  if (!id || typeof id !== "string") {
    return null
  } else {
    return id
  }
}

/**
 * Save the WebAuthn credential ID.
 */
export const saveWebAuthnCredentialId = (
  credentialId: string | null | undefined
) => {
  if (credentialId) {
    window.localStorage.setItem(
      WEBAUTHN_CREDENTIAL_ID_LOCAL_STORAGE_KEY,
      credentialId
    )
  } else {
    window.localStorage.removeItem(WEBAUTHN_CREDENTIAL_ID_LOCAL_STORAGE_KEY)
  }
}
