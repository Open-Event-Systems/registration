declare module "oauth4webapi" {
  interface TokenEndpointResponse {
    account_id?: string | null
    email?: string | null
  }
}

/**
 * The account information.
 */
export interface AccountInfo {
  id?: string | null
  email?: string | null
  scope?: string | null
}

/**
 * Verified email token response.
 */
export interface EmailTokenResponse {
  token: string
}

/**
 * Scope values.
 */
export enum Scope {
  event = "event",
  cart = "cart",
  selfService = "self-service",
  registration = "registration",
  registrationEdit = "registration:edit",
  admin = "admin",
}
