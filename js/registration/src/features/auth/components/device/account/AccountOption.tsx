import { Radio, Stack, TextInput } from "@mantine/core"

type ValueType = {
  account: "my_account" | "anonymous" | "new_account"
  email: string
}

export type AccountOptionProps = {
  value: ValueType
  onChange: (value: ValueType) => void
}

export const AccountOption = (props: AccountOptionProps) => {
  const { value, onChange } = props
  const { account, email } = value

  return (
    <Radio.Group
      defaultValue="my_account"
      value={account}
      onChange={(newValue) => {
        onChange && onChange({ ...value, account: newValue } as ValueType)
      }}
    >
      <Stack>
        <Radio value="my_account" label="My account" />
        <Radio value="anonymous" label="An anonymous account" />
        <Radio value="new_account" label="A new account with this email:" />
        <TextInput
          placeholder="Email"
          inputMode="email"
          autoComplete="email"
          disabled={account != "new_account"}
          value={email}
          onChange={(e) => {
            onChange &&
              onChange({ ...value, email: e.target.value } as ValueType)
          }}
        />
      </Stack>
    </Radio.Group>
  )
}
