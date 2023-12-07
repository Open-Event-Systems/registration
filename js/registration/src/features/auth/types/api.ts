import { DeviceAuthorizationOptions } from "#src/features/auth/components/device/auth/DeviceAuthorization"
import { AccountInfo } from "#src/features/auth/types/AccountInfo"
import { WebAuthnChallenge } from "#src/features/auth/types/WebAuthn"
import {
  UndefinedInitialDataOptions,
  UseMutationOptions,
} from "@tanstack/react-query"
import * as oauth from "oauth4webapi"

export type AuthAPI = {
  createAccount(
    clientId: string,
  ): UseMutationOptions<oauth.TokenEndpointResponse>
  readAccountInfo(): UndefinedInitialDataOptions<AccountInfo>
  createInitialRefreshToken(): UseMutationOptions<oauth.TokenEndpointResponse>
  sendVerificationEmail(): UseMutationOptions<void, Error, string>
  verifyEmail(
    email: string,
  ): UseMutationOptions<oauth.TokenEndpointResponse, Error, string>
  readWebAuthnRegistrationChallenge(): UndefinedInitialDataOptions<WebAuthnChallenge>
  completeWebAuthnRegistration(
    challenge: WebAuthnChallenge,
  ): UseMutationOptions<void, Error, string>
  readWebAuthnAuthenticationChallenge(
    credentialId: string,
  ): UndefinedInitialDataOptions<WebAuthnChallenge>
  completeWebAuthnAuthentication(
    challenge: WebAuthnChallenge,
  ): UseMutationOptions<oauth.TokenEndpointResponse, Error, string>
  readDeviceAuthRequest(
    clientId: string,
    scope?: string[],
  ): UndefinedInitialDataOptions<oauth.DeviceAuthorizationResponse>
  checkDeviceAuthRequest(
    userCode: string,
  ): UndefinedInitialDataOptions<DeviceAuthorizationOptions>
  authorizeDevice(userCode: string): UseMutationOptions<
    void,
    Error,
    {
      scope?: string[]
      new_account?: boolean
      email?: string
      require_webauthn?: boolean
    }
  >
}
