import { SignInOptionsOption } from "#src/features/auth/components/options/SignInOptionsMenu"

import { useAuthAPI, useSignInState } from "#src/features/auth/hooks"
import { Button, Stack, Text, TextInput } from "@mantine/core"
import { IconAt } from "@tabler/icons-react"
import { useMutation } from "@tanstack/react-query"
import { action } from "mobx"
import { observer, useLocalObservable } from "mobx-react-lite"
import { useEffect } from "react"

export const EmailSignInOption = () => {
  const state = useSignInState()

  return (
    <SignInOptionsOption
      label="Sign in with email"
      description="Use your email address to sign in"
      leftSection={<IconAt />}
      onClick={() => {
        state.selectOptionId("email")
      }}
    />
  )
}

/**
 * Email auth.
 */
export const EmailSignIn = observer(() => {
  const localState = useLocalObservable(() => ({
    sent: false,
    email: "",
    code: "",
  }))

  const api = useAuthAPI()
  const state = useSignInState()
  const token = state.tokenResponse?.access_token ?? ""
  const sendEmail = useMutation(api.sendVerificationEmail())
  const verifyEmail = useMutation(api.verifyEmail(token, localState.email))

  useEffect(() => {
    if (!token) {
      state.getAccount()
    }
  }, [token])

  let content

  if (!sendEmail.isSuccess) {
    content = (
      <EmailForm
        value={localState.email}
        onChange={action((v) => (localState.email = v))}
        onSubmit={async () => {
          if (!token) {
            return
          }
          sendEmail.reset()
          await sendEmail.mutateAsync({
            accessToken: token,
            email: localState.email,
          })
        }}
        error={sendEmail.error?.message}
      />
    )
  } else {
    content = (
      <CodeForm
        value={localState.code}
        onChange={action((v) => (localState.code = v))}
        onSubmit={async () => {
          if (!token) {
            return
          }
          verifyEmail.reset()
          const newToken = await verifyEmail.mutateAsync(localState.code)
          state.completeRegistration(newToken)
        }}
        error={verifyEmail.error?.message}
      />
    )
  }

  return content
})

EmailSignIn.displayName = "EmailSignIn"

const EmailForm = (props: {
  value: string
  onChange: (v: string) => void
  onSubmit: () => void
  error?: string
}) => {
  const { value, onChange, onSubmit, error } = props
  return (
    <form
      className="EmailAuth-root"
      onSubmit={(e) => {
        e.preventDefault()
        onSubmit()
      }}
    >
      <Stack className="EmailAuth-stack">
        <Text>Enter your email address.</Text>
        <TextInput
          key="email"
          inputMode="email"
          autoComplete="email"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          error={error ?? undefined}
          label="Email"
        />
        <div className="EmailAuth-spacer"></div>
        <Button type="submit">Continue</Button>
      </Stack>
    </form>
  )
}

const CodeForm = (props: {
  value: string
  onChange: (v: string) => void
  onSubmit: () => void
  error?: string
}) => {
  const { value, onChange, onSubmit, error } = props
  return (
    <form
      className="EmailAuth-root"
      onSubmit={(e) => {
        e.preventDefault()
        onSubmit()
      }}
    >
      <Stack className="EmailAuth-stack">
        <Text>
          We&apos;ve sent a code to your email address. Enter the code below.
        </Text>
        <TextInput
          key="code"
          inputMode="numeric"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          error={error}
          label="Code"
        />
        <div className="EmailAuth-spacer"></div>
        <Button type="submit">Verify</Button>
      </Stack>
    </form>
  )
}
