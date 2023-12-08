import { Scope } from "#src/features/auth/types/AccountInfo"
import { TokenEndpointResponse } from "oauth4webapi"

/**
 * Stores a token response.
 * All properties should be treated as read-only.
 */
export class AuthInfo {
  expiresAt: Date | null
  constructor(
    public tokenType: string,
    public accessToken: string,
    public refreshToken: string | null = null,
    expiresAt: Date | number | null = null,
    public scope: string | null = null,
    public accountId: string | null = null,
    public email: string | null = null,
  ) {
    if (typeof expiresAt == "number") {
      this.expiresAt = new Date(expiresAt * 1000)
    } else {
      this.expiresAt = expiresAt
    }
  }

  /**
   * Scope values, as a string array.
   */
  get scopeItems(): string[] {
    return this.scope?.split(" ") || []
  }

  /**
   * Get whether a scope is included.
   */
  hasScope(scope: Scope): boolean {
    return this.scopeItems.includes(scope)
  }

  /**
   * Create a {@link AuthInfo} from a token endpoint response.
   */
  static createFromResponse(response: TokenEndpointResponse): AuthInfo {
    let expiresAt = null
    if (response.expires_in != null) {
      const now = Math.floor(new Date().getTime() / 1000)
      expiresAt = now + response.expires_in
    }

    return new AuthInfo(
      response.token_type,
      response.access_token,
      response.refresh_token ?? null,
      expiresAt,
      response.scope ?? null,
      response.account_id ?? null,
      response.email ?? null,
    )
  }

  /**
   * Parse a {@link AuthInfo} from an object.
   *
   * @returns A {@link AuthInfo} object, or null if it could not be parsed.
   */
  static createFromObject(obj: object): AuthInfo | null {
    try {
      const parsed = obj as {
        tokenType: string
        accessToken: string
        refreshToken?: string
        expiresAt?: number
        scope?: string
        accountId?: string
        email?: string
      }

      return new AuthInfo(
        parsed.tokenType,
        parsed.accessToken,
        parsed.refreshToken ?? null,
        parsed.expiresAt ?? null,
        parsed.scope ?? null,
        parsed.accountId ?? null,
        parsed.email ?? null,
      )
    } catch (_) {
      return null
    }
  }

  /**
   * Return whether the access token is expired.
   */
  getIsExpired(): boolean {
    const now = new Date().getTime()
    return this.expiresAt != null && now >= this.expiresAt.getTime()
  }

  toJSON() {
    return {
      tokenType: this.tokenType,
      accessToken: this.accessToken,
      refreshToken: this.refreshToken,
      expiresAt:
        this.expiresAt != null
          ? Math.floor(this.expiresAt.getTime() / 1000)
          : null,
      scope: this.scope,
      accountId: this.accountId,
      email: this.email,
    }
  }
}
