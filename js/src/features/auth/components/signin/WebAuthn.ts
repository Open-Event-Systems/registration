import {
  completeWebAuthnAuthentication,
  completeWebAuthnRegistration,
  getWebAuthnAuthenticationChallenge,
} from "#src/features/auth/api.js"
import { AuthInfo } from "#src/features/auth/stores/AuthInfo.js"
import { SignInState } from "#src/features/auth/types/SignInOptions.js"
import { WebAuthnChallenge } from "#src/features/auth/types/WebAuthn.js"
import { startAuthentication, startRegistration } from "@simplewebauthn/browser"

/**
 * Perform WebAuthn registration/authentication. No actual component is rendered.
 */
export const createWebAuthnSignIn = async (
  state: SignInState
): Promise<null> => {
  if (state.isWebAuthnAvailable && state.webAuthnCredentialId) {
    // sign-in
    const challenge = await getWebAuthnAuthenticationChallenge(
      state.wretch,
      state.webAuthnCredentialId
    )
    const res = await performWebAuthnAuthentication(state, challenge)
    if (res) {
      state.handleComplete(res)
    }
  } else if (state.webAuthnRegistrationChallenge) {
    // register
    const res = await performWebAuthnRegistration(
      state,
      state.webAuthnRegistrationChallenge
    )
    if (res) {
      const [credentialId, authInfo] = res
      state.webAuthnCredentialId = credentialId
      state.handleComplete(authInfo)
    }
  }

  return null
}

export const performWebAuthnRegistration = async (
  state: SignInState,
  challenge: WebAuthnChallenge,
  emailToken?: string | null
): Promise<[string, AuthInfo] | null> => {
  let registration
  try {
    registration = await startRegistration(challenge.options)
  } catch (err) {
    console.error("WebAuthn registration failed", err)
    state.webAuthnError = true
    return null
  }

  if (!registration) {
    console.error("WebAuthn registration failed")
    state.webAuthnError = true
    return null
  }

  const result = await completeWebAuthnRegistration(state.wretch, {
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
  state: SignInState,
  challenge: WebAuthnChallenge
): Promise<AuthInfo | null> => {
  let auth
  try {
    auth = await startAuthentication(challenge.options)
  } catch (err) {
    console.error("WebAuthn authentication failed", err)
    state.webAuthnError = true
    return null
  }

  if (!auth) {
    console.error("WebAuthn authentication failed")
    state.webAuthnError = true
    return null
  }

  const result = await completeWebAuthnAuthentication(state.wretch, {
    challenge: challenge.challenge,
    result: JSON.stringify(auth),
  })

  if (result) {
    return AuthInfo.createFromResponse(result)
  } else {
    return null
  }
}
