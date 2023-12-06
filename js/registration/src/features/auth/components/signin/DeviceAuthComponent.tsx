import { DeviceAuthRequest } from "#src/features/auth/components/device/auth/DeviceAuthRequest"
import { DeviceAuthSignInRequest } from "#src/features/auth/impl/DeviceAuthRequest"
import { AuthInfo } from "#src/features/auth/stores/AuthInfo"
import { SignInOptionComponentProps } from "#src/features/auth/types/SignInOptions"
import { Container, Text } from "@mantine/core"
import { useEffect, useState } from "react"

export const DeviceAuthComponent = (
  props: SignInOptionComponentProps & { request: DeviceAuthSignInRequest },
) => {
  const { request, onComplete } = props
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    request
      .then((res) => {
        if (res == false) {
          setError("Authorization failed")
        } else {
          onComplete(AuthInfo.createFromResponse(res))
        }
      })
      .catch((err) => setError(String(err)))

    return () => {
      request.cancel()
    }
  }, [request])

  if (error) {
    return (
      <Container>
        <Text component="p">{error}</Text>
      </Container>
    )
  }

  return (
    <DeviceAuthRequest
      url={request.url}
      urlComplete={request.urlComplete}
      userCode={request.userCode}
    />
  )
}
