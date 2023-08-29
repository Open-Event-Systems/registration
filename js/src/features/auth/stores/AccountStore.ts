import {
  completeWebAuthnAuthentication,
  completeWebAuthnRegistration,
  createAccount,
  getWebAuthnAuthenticationChallenge,
  getWebAuthnRegistrationChallenge,
  sendVerificationEmail,
  verifyEmail,
} from "#src/features/auth/api.js"
import { AuthStore } from "#src/features/auth/stores/AuthStore.js"
import { AuthInfo } from "#src/features/auth/stores/AuthInfo.js"
import {
  browserSupportsWebAuthn,
  platformAuthenticatorIsAvailable,
  startAuthentication,
  startRegistration,
} from "@simplewebauthn/browser"

import type { RegistrationResponseJSON } from "@simplewebauthn/typescript-types"

import { Wretch } from "wretch"
import { action, makeAutoObservable, runInAction, when } from "mobx"
import { WebAuthnChallenge } from "#src/features/auth/types/WebAuthn.js"

/**
 * The local storage key for the stored credential ID.
 */
const WEBAUTHN_CREDENTIAL_ID_LOCAL_STORAGE_KEY = "oes-credential-id-v1"

/**
 * Options for account creation.
 */
export interface CreateAccountOptions {
  /**
   * Whether to allow a security key (non-platform authenticator) for WebAuthn.
   */
  allowSecurityKey?: boolean

  /**
   * A verified email token.
   */
  emailToken?: string
}

/**
 * Manages account creation/login.
 */
export class AccountStore {
  /**
   * Resolves when setup is finished.
   */
  ready: Promise<void>
  private _ready = false

  /**
   * WebAuthn availability and type.
   */
  isWebAuthnAvailable: "platform" | boolean = false

  /**
   * Whether WebAuthn failed.
   */
  webAuthnError = false

  /**
   * The saved WebAuthn credential ID.
   */
  webAuthnCredentialId: string | null = null

  constructor(private wretch: Wretch, private authStore: AuthStore) {
    makeAutoObservable(this, {
      ready: false,
    })

    this.ready = when(() => this._ready)
  }

  /**
   * Perform initial setup.
   */
  async setup(): Promise<void> {
    try {
      await Promise.all([this.webAuthnSetup()])
    } finally {
      runInAction(() => {
        this._ready = true
      })
    }
  }

  private async webAuthnSetup() {
    this.webAuthnCredentialId = getSavedWebAuthnCredentialId()
    const webAuthnState = await checkWebAuthnAvailability()
    runInAction(() => {
      this.isWebAuthnAvailable = webAuthnState
    })
  }

  /**
   * Create a new account without credentials and update the {@link AuthStore}.
   */
  async createBasicAccount(emailToken?: string): Promise<AuthInfo> {
    const tokenResponse = await createAccount(this.wretch, emailToken)
    const authInfo = AuthInfo.createFromResponse(tokenResponse)
    await this.authStore.setAuthInfo(authInfo)
    return authInfo
  }

  /**
   * Create an account using WebAuthn and update the {@link AuthStore}.
   * @returns The created account {@link AuthInfo} or null if unsuccessful.
   */
  async createWebAuthnAccount(
    challenge: WebAuthnChallenge,
    emailToken?: string
  ): Promise<AuthInfo | null> {
    let result
    try {
      result = await startRegistration(challenge)
    } catch (err) {
      console.error("WebAuthn registration failed:", err)
      runInAction(() => {
        this.webAuthnError = true
      })
      return null
    }

    if (result) {
      console.error("WebAuthn registration failed")
      runInAction(() => {
        this.webAuthnError = true
      })
      return null
    }

    const credentialId = result.id
    const tokenResponse = await completeWebAuthnRegistration(this.wretch, {
      challenge: challenge.challenge,
      result: JSON.stringify(result),
      email_token: emailToken,
    })

    if (!tokenResponse) {
      return null
    }

    const authInfo = AuthInfo.createFromResponse(tokenResponse)
    runInAction(() => {
      this.webAuthnCredentialId = credentialId
    })
    saveWebAuthnCredentialId(credentialId)
    return await this.authStore.setAuthInfo(authInfo)
  }

  /**
   * Attempt to authenticate.
   * @returns The {@link AuthInfo} or null if authentication failed.
   */
  async authenticate(challenge?: WebAuthnChallenge): Promise<AuthInfo | null> {
    const useWebAuthn =
      this.isWebAuthnAvailable && this.webAuthnCredentialId && challenge

    if (useWebAuthn) {
      const result = await this.performWebAuthnAuthentication(challenge)
      if (!result) {
        return null
      } else {
        return result
      }
    }

    return null
  }

  /**
   * Perform WebAuthn authentication.
   * @returns The resulting {@link AuthInfo} or null if unsuccessful.
   */
  async performWebAuthnAuthentication(
    challenge: WebAuthnChallenge
  ): Promise<AuthInfo | null> {
    let authResult
    try {
      authResult = await startAuthentication(challenge.options)
    } catch (err) {
      console.error("WebAuthn authentication failed:", err)
      runInAction(() => {
        this.webAuthnError = true
      })
      return null
    }

    if (!authResult) {
      console.error("WebAuthn authentication failed")
      runInAction(() => {
        this.webAuthnError = true
      })
      return null
    }

    const tokenResponse = await completeWebAuthnAuthentication(this.wretch, {
      challenge: challenge.challenge,
      result: JSON.stringify(authResult),
    })

    if (!tokenResponse) {
      return null
    }

    const authInfo = AuthInfo.createFromResponse(tokenResponse)

    await this.authStore.setAuthInfo(authInfo)
    return authInfo
  }
}

const checkWebAuthnAvailability = async () => {
  if (!browserSupportsWebAuthn()) {
    return false
  }

  const platformAuthAvailable = await platformAuthenticatorIsAvailable()
  return platformAuthAvailable ? "platform" : true
}

const getSavedWebAuthnCredentialId = () => {
  const id = window.localStorage.getItem(
    WEBAUTHN_CREDENTIAL_ID_LOCAL_STORAGE_KEY
  )
  if (!id || typeof id !== "string") {
    return null
  } else {
    return id
  }
}

const saveWebAuthnCredentialId = (credentialId: string | null | undefined) => {
  if (credentialId) {
    window.localStorage.setItem(
      WEBAUTHN_CREDENTIAL_ID_LOCAL_STORAGE_KEY,
      credentialId
    )
  } else {
    window.localStorage.removeItem(WEBAUTHN_CREDENTIAL_ID_LOCAL_STORAGE_KEY)
  }
}
