import {
  SignInOption,
  SignInOptionComponentProps,
  SignInState,
} from "#src/features/auth/types/SignInOptions"
import { IconDevices } from "@tabler/icons-react"
import { Wretch } from "wretch"

const CLIENT_ID = "oes"

/**
 * Perform device authorization.
 */
export class DeviceAuthSignIn implements SignInOption {
  id = "device"
  name = "Other device"
  description = "Sign in from another device"
  icon = IconDevices

  constructor(
    private wretch: Wretch,
    public clientId: string = CLIENT_ID,
    public scope: string[] | null = null,
  ) {}

  async getRender() {
    const { performDeviceAuthRequest } = await import(
      "#src/features/auth/impl/DeviceAuthRequest"
    )
    const { DeviceAuthComponent } = await import(
      "#src/features/auth/components/signin/DeviceAuthComponent"
    )
    const req = await performDeviceAuthRequest(
      this.wretch,
      this.clientId,
      this.scope ?? undefined,
    )

    const renderFunc = (props: SignInOptionComponentProps) => {
      return <DeviceAuthComponent {...props} request={req()} />
    }
    return renderFunc
  }
}

/**
 * Get a device auth sign in state.
 */
export const getDeviceAuthSignIn = async (wretch: Wretch) => {
  // TODO: config

  return new DeviceAuthSignIn(wretch)
}
