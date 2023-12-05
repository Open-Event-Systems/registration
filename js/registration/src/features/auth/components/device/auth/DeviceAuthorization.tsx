import { DeviceAuthOptions } from "#src/features/auth/components/device/auth-options/DeviceAuthOptions"
import { Button, Stack, Text, Title } from "@mantine/core"
import { IconCheck, IconX } from "@tabler/icons-react"
import { useState } from "react"

type Options = {
  account: "my_account" | "anonymous" | "new_account"
  email: string
  scope: string[]
  requireWebAuthn: boolean
}

export type DeviceAuthorizationProps = {
  client: string
  scope: string[]
  showOptions?: boolean
  onComplete?: (options: Options) => void
  onCancel?: () => void
}

export const DeviceAuthorization = (props: DeviceAuthorizationProps) => {
  const { client, scope, showOptions, onComplete, onCancel } = props

  const [options, setOptions] = useState<Options>({
    account: "my_account",
    email: "",
    requireWebAuthn: false,
    scope: scope,
  })

  return (
    <Stack className="DeviceAuthorization-root">
      <Title order={3}>Authorize Device</Title>
      <Text>
        <b>Application:</b> {client}
      </Text>
      {showOptions && (
        <DeviceAuthOptions value={options} onChange={setOptions} />
      )}
      <div className="DeviceAuthorization-spacer"></div>
      <Button
        className="DeviceAuthorization-confirm"
        variant="filled"
        leftSection={<IconCheck />}
        onClick={() => {
          onComplete && onComplete(options)
        }}
      >
        Authorize
      </Button>
      <Button
        className="DeviceAuthorization-cancel"
        variant="outline"
        leftSection={<IconX />}
        color="red"
        onClick={onCancel}
      >
        Cancel
      </Button>
    </Stack>
  )
}
