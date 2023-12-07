import {
  AccountInfo,
  EmailTokenResponse,
} from "#src/features/auth/types/AccountInfo"
import {
  WebAuthnChallenge,
  WebAuthnChallengeResult,
} from "#src/features/auth/types/WebAuthn"
import { AuthAPI } from "#src/features/auth/types/api"
import { QueryClient } from "@tanstack/react-query"
import * as oauth from "oauth4webapi"
import { Wretch } from "wretch"
import formUrl from "wretch/addons/formUrl"

export const createAuthAPI = (
  wretch: Wretch,
  authWretch: Wretch,
  client: QueryClient,
): AuthAPI => {
  wretch = wretch.url("/auth")
  authWretch = authWretch.url("/auth")
  return {
    createAccount(clientId) {
      return {
        mutationKey: ["auth", "create-account"],
        async mutationFn() {
          return await wretch
            .url("/account/create")
            .addon(formUrl)
            .formUrl({ client_id: clientId })
            .post()
            .json()
        },
      }
    },
    readAccountInfo() {
      return {
        queryKey: ["auth", "account-info"],
        async queryFn() {
          return await authWretch.url("/account").get().json()
        },
      }
    },
    createInitialRefreshToken() {
      return {
        async mutationFn() {
          return await authWretch.url("/refresh-token").post().json()
        },
      }
    },
    sendVerificationEmail() {
      return {
        mutationKey: ["auth", "email"],
        async mutationFn(email) {
          await authWretch
            .url("/email/send")
            .json({ email: email })
            .post()
            .res()
        },
      }
    },
    verifyEmail(email) {
      return {
        mutationKey: ["auth", "email"],
        async mutationFn(code) {
          return await authWretch
            .url("/email/verify")
            .json({ email: email, code: code })
            .post()
            .json()
        },
      }
    },
    readWebAuthnRegistrationChallenge() {
      return {
        queryKey: ["auth", "webauthn", "register"],
        async queryFn() {
          return await authWretch.url("/webauthn/register").get().json()
        },
        staleTime: 600000,
      }
    },
    completeWebAuthnRegistration(challenge) {
      return {
        mutationKey: ["auth", "webauthn", "register"],
        async mutationFn(result) {
          await authWretch
            .url("/webauthn/register")
            .json({ challenge: challenge.challenge, result: result })
            .post().res
        },
      }
    },
    readWebAuthnAuthenticationChallenge(credentialId) {
      return {
        queryKey: ["auth", "webauthn", "authenticate", credentialId],
        async queryFn() {
          return await wretch
            .url(`/webauthn/authenticate/${credentialId}`)
            .get()
            .json()
        },
        staleTime: 600000,
      }
    },
    completeWebAuthnAuthentication(challenge) {
      return {
        mutationKey: ["auth", "webauthn", "register"],
        async mutationFn(result) {
          return await wretch
            .url("/webauthn/register")
            .json({ challenge: challenge.challenge, result: result })
            .post()
            .json()
        },
      }
    },
    readDeviceAuthRequest(clientId, scope) {
      return {
        queryKey: ["auth", "authorize-device"],
        async queryFn() {
          const req: Record<string, unknown> = {
            client_id: clientId,
          }

          if (scope) {
            req.scope = scope
          }

          return await wretch
            .url("/authorize-device")
            .addon(formUrl)
            .formUrl(req)
            .post()
            .json()
        },
        staleTime: 180000,
      }
    },
    checkDeviceAuthRequest(userCode) {
      return {
        queryKey: ["auth", "check-authorize-device", userCode],
        async queryFn() {
          return await authWretch
            .url("/check-authorize-device")
            .json({ user_code: userCode })
            .post()
            .json()
        },
      }
    },
    authorizeDevice(userCode) {
      return {
        mutationKey: ["auth", "complete-authorize-device"],
        async mutationFn(options) {
          const req: Record<string, unknown> = {
            user_code: userCode,
          }

          if (options.scope) {
            req.scope = options.scope
          }

          if (options.new_account) {
            req.new_account = options.new_account
          }

          if (options.email) {
            req.email = options.email
          }

          if (options.require_webauthn) {
            req.require_webauthn = options.require_webauthn
          }

          await authWretch
            .url("/complete-authorize-device")
            .json(req)
            .post()
            .res()
        },
      }
    },
  }
}

/**
 * Get the current account information.
 */
export const getAccountInfo = async (wretch: Wretch): Promise<AccountInfo> => {
  return await wretch.url("/auth/account").get().json<AccountInfo>()
}

/**
 * Send a verification code to the given email.
 */
export const sendVerificationEmail = async (
  wretch: Wretch,
  email: string,
): Promise<void> => {
  return await wretch
    .url("/auth/email/send")
    .json({ email: email })
    .post()
    .res()
}

/**
 * Verify an email.
 */
export const verifyEmail = async (
  wretch: Wretch,
  email: string,
  code: string,
): Promise<EmailTokenResponse | null> => {
  return await wretch
    .url("/auth/email/verify")
    .json({ email: email, code: code })
    .post()
    .forbidden(() => null)
    .json<EmailTokenResponse>()
}

/**
 * Create a new account without credentials.
 */
export const createAccount = async (
  wretch: Wretch,
  emailToken?: string | null,
): Promise<oauth.TokenEndpointResponse> => {
  return await wretch
    .url("/auth/account/create")
    .json({
      email_token: emailToken ?? null,
    })
    .post()
    .json<oauth.TokenEndpointResponse>()
}

/**
 * Get WebAuthn a registration challenge and options.
 */
export const getWebAuthnRegistrationChallenge = async (
  wretch: Wretch,
): Promise<WebAuthnChallenge> => {
  return await wretch
    .url("/auth/webauthn/register")
    .get()
    .json<WebAuthnChallenge>()
}

/**
 * Complete a WebAuthn registration.
 */
export const completeWebAuthnRegistration = async (
  wretch: Wretch,
  request: WebAuthnChallengeResult,
): Promise<oauth.TokenEndpointResponse | null> => {
  return await wretch
    .url("/auth/webauthn/register")
    .json(request)
    .post()
    .badRequest(() => null)
    .json<oauth.TokenEndpointResponse>()
}

/**
 * Get a challenge to authenticate using the given credential ID.
 */
export const getWebAuthnAuthenticationChallenge = async (
  wretch: Wretch,
  credentialId: string,
): Promise<WebAuthnChallenge> => {
  return await wretch
    .url(`/auth/webauthn/authenticate/${credentialId}`)
    .get()
    .json<WebAuthnChallenge>()
}

/**
 * Complete WebAuthn authentication.
 */
export const completeWebAuthnAuthentication = async (
  wretch: Wretch,
  request: WebAuthnChallengeResult,
): Promise<oauth.TokenEndpointResponse | null> => {
  return await wretch
    .url("/auth/webauthn/authenticate")
    .json(request)
    .post()
    .forbidden(() => null)
    .json<oauth.TokenEndpointResponse>()
}
