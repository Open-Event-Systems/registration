import {
  createAccount,
  getWebAuthnRegistrationChallenge,
  sendVerificationEmail,
  verifyEmail,
} from "#src/features/auth/api"
import {
  SignInOptionsMenu,
  SignInOptionsOption,
} from "#src/features/auth/components/options/SignInOptionsMenu"
import {
  getPlatformWebAuthnDetails,
  getWebAuthnAvailability,
  performWebAuthnRegistration,
  saveWebAuthnCredentialId,
} from "#src/features/auth/components/signin/WebAuthn"
import { useAuth, useAuthAPI, useSignInState } from "#src/features/auth/hooks"
import { AuthInfo } from "#src/features/auth/stores/AuthInfo"
import { JS_CLIENT_ID } from "#src/features/auth/stores/AuthStore"
import {
  SignInOptionComponentProps,
  SignInOption,
} from "#src/features/auth/types/SignInOptions"
import { WebAuthnChallenge } from "#src/features/auth/types/WebAuthn"
import { useLocation, useNavigate } from "#src/hooks/location"
import { Box, Button, Stack, Text, TextInput, useProps } from "@mantine/core"
import { IconAt, IconUserOff } from "@tabler/icons-react"
import { useIsMutating, useMutation } from "@tanstack/react-query"
import clsx from "clsx"
import { action, makeAutoObservable, runInAction, when } from "mobx"
import { observer, useLocalObservable } from "mobx-react-lite"
import { ComponentPropsWithRef, useEffect } from "react"
import { Wretch } from "wretch"

declare module "#src/hooks/location" {
  interface LocationState {
    emailAuthEmail?: string
  }
}

enum Step {
  send = "send",
  verify = "verify",
  complete = "complete",
}

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

class EmailSignInState {
  email = ""
  code = ""
  step = Step.send
  error: string | null = null
  emailToken: string | null = null
  webAuthnChallenge: WebAuthnChallenge | null = null

  constructor(private wretch: Wretch) {
    makeAutoObservable(this)
  }

  async sendEmail(email: string) {
    this.error = null
    try {
      await sendVerificationEmail(this.wretch, email)
      runInAction(() => {
        this.step = Step.verify
      })
    } catch (e) {
      runInAction(() => {
        this.error = `${e}`
      })
    }
  }

  async verifyEmail(email: string, code: string) {
    this.error = null
    try {
      const res = await verifyEmail(this.wretch, email, code)
      runInAction(() => {
        if (res) {
          this.emailToken = res.token
          this.step = Step.complete
        } else {
          this.error = "Try again"
        }
      })
    } catch (_e) {
      runInAction(() => {
        this.error = "An error occurred"
      })
    }
  }

  async create() {
    const result = await createAccount(this.wretch, this.emailToken)
    if (result) {
      return AuthInfo.createFromResponse(result)
    } else {
      return null
    }
  }
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
