import { AccountOption } from "#src/features/auth/components/device/account/AccountOption"
import { ScopeSelect } from "#src/features/auth/components/device/scopes/ScopeSelect"
import { Box, Checkbox, Stack, Text } from "@mantine/core"

type Options = {
  scope: string[]
  account: "my_account" | "anonymous" | "new_account"
  email: string
  requireWebAuthn: boolean
}

export type DeviceAuthOptionsProps = {
  value: Options
  onChange: (value: Options) => void
}

export const DeviceAuthOptions = (props: DeviceAuthOptionsProps) => {
  const { value, onChange } = props

  return (
    <Stack className="DeviceAuthOptions-root">
      <Text>Authorize with:</Text>
      <Box className="DeviceAuthOptions-section">
        <AccountOption
          value={{ account: value.account, email: value.email }}
          onChange={(newValue) => onChange({ ...value, ...newValue })}
        />
      </Box>
      <Text>Security</Text>
      <Box className="DeviceAuthOptions-section">
        <Checkbox
          label="Require WebAuthn to stay signed in"
          checked={value.requireWebAuthn}
          onChange={(e) =>
            onChange({ ...value, requireWebAuthn: e.target.checked })
          }
        />
      </Box>
      <Text>Permissions:</Text>
      <Box className="DeviceAuthOptions-section">
        <ScopeSelect
          selected={value.scope}
          onChange={(scope) => onChange({ ...value, scope: scope })}
        />
      </Box>
    </Stack>
  )
}
