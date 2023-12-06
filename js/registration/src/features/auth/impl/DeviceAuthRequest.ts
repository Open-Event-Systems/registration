import { Wretch } from "wretch"
import { formUrlAddon } from "wretch/addons"
import * as oauth from "oauth4webapi"

const GRANT_TYPE = "urn:ietf:params:oauth:grant-type:device_code"

export class DeviceAuthSignInRequest {
  private canceled = false
  private promise: Promise<oauth.TokenEndpointResponse | false>

  constructor(
    private wretch: Wretch,
    public clientId: string,
    public deviceCode: string,
    public userCode: string,
    public url: string,
    public urlComplete: string,
  ) {
    this.promise = this.poll()
  }

  then<T = oauth.TokenEndpointResponse | false, T2 = never>(
    onfulfilled?:
      | ((value: oauth.TokenEndpointResponse | false) => T | PromiseLike<T>)
      | null,
    onrejected?: ((error: unknown) => T2 | PromiseLike<T2>) | null,
  ): Promise<T | T2> {
    return this.promise.then(onfulfilled, onrejected)
  }

  cancel() {
    this.canceled = true
  }

  private async poll() {
    while (!this.canceled) {
      const res = await this.pollOnce()
      if (res === true) {
        await new Promise((r) => window.setTimeout(r, 5000))
        continue
      } else {
        return res
      }
    }
    return false
  }

  private async pollOnce() {
    const req = this.wretch.addon(formUrlAddon).url("/auth/token").formUrl({
      grant_type: GRANT_TYPE,
      client_id: this.clientId,
      device_code: this.deviceCode,
    })

    const res = await req
      .post()
      .badRequest((err) => {
        const errCode = err.json ? err.json["error"] : undefined
        if (errCode == "authorization_pending") {
          return true
        } else if (errCode == "access_denied" || errCode == "expired_token") {
          return false
        } else {
          throw err
        }
      })
      .json<oauth.TokenEndpointResponse | boolean>()

    return res
  }
}

/**
 * Return a promise for a function to get a device auth request.
 */
export const performDeviceAuthRequest = async (
  wretch: Wretch,
  clientId: string,
  scope?: string[],
): Promise<() => DeviceAuthSignInRequest> => {
  const body: Record<string, unknown> = {
    client_id: clientId,
  }

  if (scope) {
    body.scope = scope.join(" ")
  }

  const response = await wretch
    .addon(formUrlAddon)
    .url("/auth/authorize-device")
    .formUrl(body)
    .post()
    .json<oauth.DeviceAuthorizationResponse>()

  const req = new DeviceAuthSignInRequest(
    wretch,
    clientId,
    response.device_code,
    response.user_code,
    response.verification_uri,
    response.verification_uri_complete ?? response.verification_uri,
  )
  return () => req
}
