import {
  createAccount,
  sendVerificationEmail,
  verifyEmail,
} from "#src/features/auth/api.js"
import { SigninOptionsMenu } from "#src/features/auth/components/SigninOptionsMenu.js"
import { performWebAuthnRegistration } from "#src/features/auth/components/signin/WebAuthn.js"
import { getPlatformWebAuthnDetails } from "#src/features/auth/signInOptions.js"
import { AuthInfo } from "#src/features/auth/stores/AuthInfo.js"
import { SignInState } from "#src/features/auth/types/SignInOptions.js"
import { WebAuthnChallenge } from "#src/features/auth/types/WebAuthn.js"
import {
  Button,
  DefaultProps,
  Selectors,
  Stack,
  Text,
  TextInput,
  createStyles,
  useComponentDefaultProps,
} from "@mantine/core"
import { IconUserOff } from "@tabler/icons-react"
import { action, makeAutoObservable, runInAction } from "mobx"
import { observer, useLocalObservable } from "mobx-react-lite"
import { ComponentPropsWithRef } from "react"

declare module "#src/hooks/location.js" {
  interface LocationState {
    emailAuthEmail?: string
  }
}

class EmailAuthState {
  email = ""
  emailInput = ""
  code = ""
  emailToken: string | null = null
  error: string | null = null

  webAuthnRegistrationChallenge: WebAuthnChallenge | null = null

  constructor(private signInState: SignInState) {
    makeAutoObservable(this)
  }

  async sendEmail(email: string) {
    this.error = null
    try {
      await sendVerificationEmail(this.signInState.wretch, email)
      runInAction(() => {
        this.email = email
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
      const res = await verifyEmail(this.signInState.wretch, email ?? "", code)
      runInAction(() => {
        if (res) {
          this.emailToken = res.token
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
    const result = await createAccount(this.signInState.wretch, this.emailToken)
    if (result) {
      return AuthInfo.createFromResponse(result)
    } else {
      return null
    }
  }
}

const useStyles = createStyles({
  root: {
    padding: "1rem",
  },
  stack: {},
})

export type EmailAuthProps = {
  state: SignInState
} & Omit<ComponentPropsWithRef<"form">, "onSubmit"> &
  DefaultProps<Selectors<typeof useStyles>>

/**
 * Email auth.
 */
const EmailAuth = observer((props: EmailAuthProps) => {
  const { className, classNames, styles, unstyled, state, ...other } =
    useComponentDefaultProps("EmailAuth", {}, props)

  const { classes, cx } = useStyles(undefined, {
    name: "EmailAuth",
    classNames,
    styles,
    unstyled,
  })

  const emailAuthState = useLocalObservable(() => new EmailAuthState(state))

  const webAuthnAllowed = state.isWebAuthnAvailable == "platform"

  let content

  if (emailAuthState.emailToken && webAuthnAllowed) {
    const webAuthnDetails = getPlatformWebAuthnDetails(
      window.navigator.userAgent
    )

    // show sign in options
    content = (
      <Stack className={classes.stack}>
        <Text>You&apos;ve successfully verified your email.</Text>
        <SigninOptionsMenu
          options={[
            {
              id: "platformWebAuthn",
              name: webAuthnDetails.emailName,
              description: webAuthnDetails.emailDescription,
              icon: webAuthnDetails.icon,
              factory: () => Promise.resolve(null),
            },
            {
              id: "email",
              name: webAuthnDetails.emailSkip,
              icon: IconUserOff,
              factory: () => Promise.resolve(null),
            },
          ]}
          onSelect={(id) => {
            if (state.loading) {
              return
            }

            state.loading = true

            if (
              id == "platformWebAuthn" &&
              emailAuthState.webAuthnRegistrationChallenge
            ) {
              performWebAuthnRegistration(
                state,
                emailAuthState.webAuthnRegistrationChallenge,
                emailAuthState.emailToken
              )
                .then((res) => {
                  if (res) {
                    const [credentialId, authInfo] = res
                    state.webAuthnCredentialId = credentialId
                    state.handleComplete(authInfo)
                  }
                })
                .finally(() => (state.loading = false))
            } else {
              emailAuthState
                .create()
                .then((res) => {
                  if (res) {
                    state.handleComplete(res)
                  }
                })
                .finally(() => (state.loading = false))
            }
          }}
          OptionProps={{
            type: "submit",
          }}
        />
      </Stack>
    )
  } else if (emailAuthState.email) {
    // ask for code
    content = (
      <Stack className={classes.stack}>
        <Text>
          We&apos;ve sent a code to your email address. Enter the code below.
        </Text>
        <TextInput
          key="code"
          inputMode="numeric"
          value={emailAuthState.code}
          onChange={action((e) => (emailAuthState.code = e.target.value))}
          error={emailAuthState.error || undefined}
          label="Code"
        />
        <Button type="submit">Verify</Button>
      </Stack>
    )
  } else {
    // ask for email
    content = (
      <Stack className={classes.stack}>
        <Text>Enter your email address.</Text>
        <TextInput
          key="email"
          inputMode="email"
          autoComplete="email"
          value={emailAuthState.emailInput}
          onChange={action((e) => (emailAuthState.emailInput = e.target.value))}
          error={emailAuthState.error ?? undefined}
          label="Email"
        />
        <Button type="submit">Continue</Button>
      </Stack>
    )
  }

  return (
    <form
      className={cx(classes.root, className)}
      {...other}
      onSubmit={(e) => {
        e.preventDefault()
        if (state.loading) {
          return
        }

        if (emailAuthState.emailToken) {
          // do nothing
        } else if (emailAuthState.email) {
          state.loading = true
          emailAuthState
            .verifyEmail(emailAuthState.email, emailAuthState.code)
            .then(() => {
              if (emailAuthState.emailToken) {
                if (!webAuthnAllowed) {
                  // if webauthn isn't allowed, complete the sign in now
                  return emailAuthState.create().then((authInfo) => {
                    if (authInfo) {
                      state.handleComplete(authInfo)
                    }
                  })
                }
              }
            })
            .finally(() => (state.loading = false))
        } else {
          state.loading = true
          emailAuthState
            .sendEmail(emailAuthState.emailInput)
            .finally(() => (state.loading = false))
        }
      }}
    >
      {content}
    </form>
  )
})

EmailAuth.displayName = "EmailAuth"

export const createEmailAuth = () => Promise.resolve(EmailAuth)
