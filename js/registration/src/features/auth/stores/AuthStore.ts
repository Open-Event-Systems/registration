import { action, makeAutoObservable, runInAction, when } from "mobx"
import * as oauth from "oauth4webapi"
import { Wretch } from "wretch"
import { getRetryMiddleware } from "#src/features/auth/authMiddleware"
import { AuthInfo } from "#src/features/auth/stores/AuthInfo"

/**
 * The client ID of the main JS app.
 */
export const JS_CLIENT_ID = "oes"

/**
 * The local storage key for the auth data.
 */
const LOCAL_STORAGE_KEY = "oes-auth-data-v1"

/**
 * Stores auth status/tokens.
 */
export class AuthStore {
  /**
   * A {@link Wretch} with auth middlewares added.
   */
  authWretch: Wretch

  /**
   * Whether initial setup is complete.
   */
  ready = false

  private _authInfo: AuthInfo | null = null
  private authInfoPromise: Promise<AuthInfo | null> | null = null

  private client: oauth.Client
  private authServer: oauth.AuthorizationServer

  constructor(
    serverBaseURL: URL,
    public wretch: Wretch,
  ) {
    this.authWretch = wretch.middlewares([
      getRetryMiddleware(serverBaseURL, this),
    ])

    this.client = {
      client_id: JS_CLIENT_ID,
      token_endpoint_auth_method: "none",
    }

    let baseURLStr = serverBaseURL.toString()
    if (baseURLStr.endsWith("/")) {
      baseURLStr = baseURLStr.substring(0, baseURLStr.length - 1)
    }

    this.authServer = {
      issuer: JS_CLIENT_ID, // TODO
      token_endpoint: `${baseURLStr}/auth/token`,
    }

    makeAutoObservable<this, "client" | "authServer">(this, {
      wretch: false,
      authWretch: false,
      client: false,
      authServer: false,
    })

    // update the auth info if another window updates it in storage
    window.addEventListener("storage", (e) => {
      if (e.key == LOCAL_STORAGE_KEY && e.newValue) {
        try {
          const obj = JSON.parse(e.newValue)
          const loaded = AuthInfo.createFromObject(obj)
          if (
            loaded &&
            !loaded.getIsExpired() &&
            loaded.accessToken != this.authInfo?.accessToken
          ) {
            runInAction(() => {
              const curPromise = this.authInfoPromise ?? Promise.resolve(null)
              this.authInfoPromise = curPromise.then(
                action(() => {
                  this._authInfo = loaded
                  return loaded
                }),
              )
            })
          }
        } catch (_) {
          // ignore
        }
      }
    })
  }

  /**
   * The current access token.
   */
  get accessToken(): string | null {
    return this.authInfo?.accessToken ?? null
  }

  /**
   * The current email.
   */
  get email(): string | null {
    return this.authInfo?.email ?? null
  }

  /**
   * The current access token scope.
   */
  get scope(): string[] | null {
    if (this.authInfo?.scope != null) {
      return this.authInfo.scope.split(" ")
    } else {
      return null
    }
  }

  /**
   * The current {@link AuthInfo}.
   */
  get authInfo(): AuthInfo | null {
    return this._authInfo
  }

  set authInfo(value: AuthInfo | null) {
    this._authInfo = value
    this.authInfoPromise = (this.authInfoPromise ?? Promise.resolve(null)).then(
      () => value,
    )
    saveAuthInfo(value)
  }

  /**
   * Remove auth info and reload.
   */
  signOut() {
    saveAuthInfo(null)
    window.location.reload()
  }

  /**
   * Get a promise that resolves to an {@link AuthInfo}.
   */
  async getAuthInfo(): Promise<AuthInfo> {
    if (!this.authInfoPromise) {
      this.authInfoPromise = this.load()
    }

    // wait for any load/refresh operation to finish
    let promise = this.authInfoPromise
    let result = await promise
    while (!result) {
      await when(() => this.authInfoPromise != promise)
      promise = this.authInfoPromise
      result = await promise
    }
    return result
  }

  /**
   * Load a saved token from storage.
   * @returns The loaded token, or null if not found/not usable.
   */
  async load(): Promise<AuthInfo | null> {
    if (!this.authInfoPromise) {
      this.authInfoPromise = this._load()
    }

    return await this.authInfoPromise
  }

  private async _load(): Promise<AuthInfo | null> {
    const loaded = loadAuthInfo()
    let result = null

    if (loaded) {
      if (loaded.getIsExpired()) {
        const refreshed = await this._refresh(loaded)
        if (refreshed) {
          result = refreshed
          runInAction(() => {
            this._authInfo = refreshed
          })
          saveAuthInfo(result)
        }
      } else {
        result = loaded
        runInAction(() => {
          this._authInfo = loaded
        })
      }
    }

    runInAction(() => {
      this.ready = true
    })
    return result
  }

  /**
   * Attempt to refresh the current {@link AuthInfo}.
   */
  async attemptRefresh(): Promise<AuthInfo | null> {
    const curPromise = this.authInfoPromise ?? Promise.resolve(null)
    const refreshInfo = this._authInfo

    this.authInfoPromise = curPromise.then(async (curInfo) => {
      if (
        curInfo &&
        (!curInfo?.accessToken ||
          curInfo.accessToken == refreshInfo?.accessToken)
      ) {
        const refreshed = await this._refresh(curInfo)
        if (refreshed) {
          runInAction(() => {
            this._authInfo = refreshed
            saveAuthInfo(refreshed)
          })
        } else {
          runInAction(() => {
            this._authInfo = null // refresh failed, discard auth info
            saveAuthInfo(null)
          })
        }
        return refreshed
      } else {
        // don't refresh if something else updated the authinfo in the meantime
        return curInfo
      }
    })

    return await this.authInfoPromise
  }

  /** OAuth refresh. */
  private async _refresh(authToken: AuthInfo): Promise<AuthInfo | null> {
    if (!authToken.refreshToken) {
      return null
    }

    const resp = await oauth.refreshTokenGrantRequest(
      this.authServer,
      this.client,
      authToken.refreshToken,
    )

    const parsed = await oauth.processRefreshTokenResponse(
      this.authServer,
      this.client,
      resp,
    )

    if (oauth.isOAuth2Error(parsed)) {
      return null
    }

    return AuthInfo.createFromResponse(parsed)
  }
}

/**
 * Save the {@link AuthInfo} to local storage.
 */
const saveAuthInfo = (info: AuthInfo | null) => {
  if (info) {
    const stringified = JSON.stringify(info)
    window.localStorage.setItem(LOCAL_STORAGE_KEY, stringified)
  } else {
    window.localStorage.removeItem(LOCAL_STORAGE_KEY)
  }
}

/**
 * Load the {@link AuthInfo} from local storage.
 */
const loadAuthInfo = (): AuthInfo | null => {
  const stringified = window.localStorage.getItem(LOCAL_STORAGE_KEY)
  if (stringified) {
    try {
      const obj = JSON.parse(stringified)
      return AuthInfo.createFromObject(obj)
    } catch (_) {
      return null
    }
  } else {
    return null
  }
}
