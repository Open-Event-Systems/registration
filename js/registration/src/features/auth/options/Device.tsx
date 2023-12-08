import { DeviceAuthRequest } from "#src/features/auth/components/device/auth/DeviceAuthRequest"
import { SignInOptionsOption } from "#src/features/auth/components/options/SignInOptionsMenu"
import { useAuthAPI, useSignInState } from "#src/features/auth/hooks"
import { JS_CLIENT_ID } from "#src/features/auth/stores/AuthStore"
import { Container, Text } from "@mantine/core"
import { IconDevices } from "@tabler/icons-react"
import { useQuery } from "@tanstack/react-query"
import { useEffect } from "react"

export const DeviceAuthOption = () => {
  const state = useSignInState()

  return (
    <SignInOptionsOption
      label="Other device"
      description="Sign in from another device"
      leftSection={<IconDevices />}
      onClick={() => {
        state.selectOptionId("device")
      }}
    />
  )
}

export const DeviceAuthComponent = () => {
  const api = useAuthAPI()
  const state = useSignInState()

  const clientId = JS_CLIENT_ID

  // TODO: get client ID
  const deviceAuthQuery = useQuery(api.readDeviceAuthRequest(clientId))
  const deviceAuthResult = useQuery({
    ...api.completeDeviceAuth(
      clientId,
      deviceAuthQuery.data?.device_code ?? "",
    ),
    enabled: !!deviceAuthQuery.data?.device_code,
  })

  useEffect(() => {
    if (deviceAuthResult.isSuccess && deviceAuthResult.data) {
      state.completeRegistration(deviceAuthResult.data)
    }
  }, [deviceAuthResult.isSuccess, deviceAuthResult.data])

  if (deviceAuthResult.error) {
    return (
      <Container>
        <Text component="p">Authorization failed.</Text>
      </Container>
    )
  }

  if (!deviceAuthQuery.isSuccess) {
    return null
  }

  return (
    <DeviceAuthRequest
      url={deviceAuthQuery.data.verification_uri}
      urlComplete={
        deviceAuthQuery.data.verification_uri_complete ??
        deviceAuthQuery.data.verification_uri
      }
      userCode={deviceAuthQuery.data.user_code}
    />
  )
}
