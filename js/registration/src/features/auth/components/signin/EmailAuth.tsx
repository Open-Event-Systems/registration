import {
  createAccount,
  getWebAuthnRegistrationChallenge,
  sendVerificationEmail,
  verifyEmail,
} from "#src/features/auth/api"
import { SignInOptionsMenu } from "#src/features/auth/components/options/SignInOptionsMenu"
import {
  getPlatformWebAuthnDetails,
  getWebAuthnAvailability,
  performWebAuthnRegistration,
  saveWebAuthnCredentialId,
} from "#src/features/auth/components/signin/WebAuthn"
import { AuthInfo } from "#src/features/auth/stores/AuthInfo"
import {
  SignInOptionComponentProps,
  SignInOption,
} from "#src/features/auth/types/SignInOptions"
import { WebAuthnChallenge } from "#src/features/auth/types/WebAuthn"
import { Button, Stack, Text, TextInput, useProps } from "@mantine/core"
import { IconAt, IconUserOff } from "@tabler/icons-react"
import clsx from "clsx"
import { action, makeAutoObservable, runInAction } from "mobx"
import { observer, useLocalObservable } from "mobx-react-lite"
import { ComponentPropsWithRef } from "react"
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

class EmailSignIn implements SignInOption {
  id = "email"
  name = "Sign in with email"
  description = "Use your email address to sign in"
  icon = IconAt

  constructor(private wretch: Wretch) {
    makeAutoObservable(this)
  }

  async getRender() {
    const webAuthnAvailable = await getWebAuthnAvailability()
    const render = (props: SignInOptionComponentProps) => (
      <EmailAuth
        webAuthn={webAuthnAvailable == "platform"}
        state={this}
        wretch={this.wretch}
        {...props}
      />
    )
    return render
  }
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

export type EmailAuthProps = {
  state: EmailSignIn
  wretch: Wretch
  webAuthn: boolean
} & SignInOptionComponentProps &
  Omit<ComponentPropsWithRef<"form">, "onSubmit">

/**
 * Email auth.
 */
const EmailAuth = observer((props: EmailAuthProps) => {
  const {
    className,
    state: _state,
    webAuthn,
    wretch,
    loading,
    onComplete,
    setLoading,
    ...other
  } = useProps("EmailAuth", {}, props)

  const localState = useLocalObservable(() => new EmailSignInState(wretch))

  let content

  if (localState.step == Step.complete && webAuthn) {
    const webAuthnDetails = getPlatformWebAuthnDetails(
      window.navigator.userAgent,
    )

    // show sign in options
    content = (
      <Stack className={clsx("EmailAuth-stack")}>
        <Text>You&apos;ve successfully verified your email.</Text>
        <SignInOptionsMenu
          options={[
            {
              id: "platformWebAuthn",
              name: webAuthnDetails.emailName,
              description: webAuthnDetails.emailDescription,
              icon: webAuthnDetails.icon,
              async getRender() {
                return null
              },
            },
            {
              id: "email",
              name: webAuthnDetails.emailSkip,
              description: null,
              icon: IconUserOff,
              async getRender() {
                return null
              },
            },
          ]}
          onSelect={(id) => {
            if (loading) {
              return
            }

            setLoading(true)

            if (id == "platformWebAuthn" && localState.webAuthnChallenge) {
              performWebAuthnRegistration(
                wretch,
                localState.webAuthnChallenge,
                localState.emailToken,
              )
                .then((res) => {
                  if (res) {
                    const [credentialId, authInfo] = res
                    saveWebAuthnCredentialId(credentialId)
                    onComplete(authInfo)
                  }
                })
                .finally(() => setLoading(false))
            } else {
              localState
                .create()
                .then((res) => {
                  if (res) {
                    onComplete(res)
                  }
                })
                .finally(() => setLoading(false))
            }
          }}
          OptionProps={{
            type: "submit",
          }}
        />
      </Stack>
    )
  } else if (
    localState.step == Step.verify ||
    localState.step == Step.complete
  ) {
    // ask for code
    content = (
      <Stack className={clsx("EmailAuth-stack")}>
        <Text>
          We&apos;ve sent a code to your email address. Enter the code below.
        </Text>
        <TextInput
          key="code"
          inputMode="numeric"
          value={localState.code}
          onChange={action((e) => (localState.code = e.target.value))}
          error={localState.error || undefined}
          label="Code"
        />
        <Button type="submit">Verify</Button>
      </Stack>
    )
  } else if (localState.step == Step.send) {
    // ask for email
    content = (
      <Stack className={clsx("EmailAuth-stack")}>
        <Text>Enter your email address.</Text>
        <TextInput
          key="email"
          inputMode="email"
          autoComplete="email"
          value={localState.email}
          onChange={action((e) => (localState.email = e.target.value))}
          error={localState.error ?? undefined}
          label="Email"
        />
        <Button type="submit">Continue</Button>
      </Stack>
    )
  }

  return (
    <form
      className={clsx("EmailAuth-root", className)}
      {...other}
      onSubmit={(e) => {
        e.preventDefault()
        if (loading) {
          return
        }

        if (localState.step == Step.verify) {
          setLoading(true)
          localState
            .verifyEmail(localState.email, localState.code)
            .then(() => {
              if (localState.emailToken) {
                if (webAuthn) {
                  return getWebAuthnRegistrationChallenge(wretch).then(
                    action((challenge) => {
                      localState.webAuthnChallenge = challenge
                      localState.step = Step.complete
                    }),
                  )
                } else {
                  return localState.create().then((authInfo) => {
                    if (authInfo) {
                      onComplete(authInfo)
                    }
                  })
                }
              }
            })
            .finally(() => setLoading(false))
        } else if (localState.step == Step.send) {
          setLoading(true)
          localState
            .sendEmail(localState.email)
            .finally(() => setLoading(false))
        }
      }}
    >
      {content}
    </form>
  )
})

EmailAuth.displayName = "EmailAuth"

/**
 * Get an email sign in state
 */
export const getEmailSignIn = async (wretch: Wretch) => new EmailSignIn(wretch)
