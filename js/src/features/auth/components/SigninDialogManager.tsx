import { EmailAuth } from "#src/features/auth/components/EmailAuth.js"
import { SigninDialog } from "#src/features/auth/components/SigninDialog.js"
import {
  SigninOptionType,
  SigninOptions,
} from "#src/features/auth/components/SigninOptions.js"
import { useAccountStore, useAuth } from "#src/features/auth/hooks.js"
import { AccountStore } from "#src/features/auth/stores/AccountStore.js"
import { WebAuthnChallenge } from "#src/features/auth/types/WebAuthn.js"
import { useNavigate } from "#src/hooks/location.js"
import { useLocation } from "#src/hooks/location.js"
import { isWretchError } from "#src/util/api.js"
import { observer } from "mobx-react-lite"
import { useEffect, useState } from "react"

declare module "#src/hooks/location.js" {
  interface LocationState {
    showEmailAuth?: boolean
  }
}

/**
 * Manages sign-in dialog and state.
 */
export const SigninDialogManager = observer(() => {
  const auth = useAuth()
  const accountStore = useAccountStore()
  const loc = useLocation()
  const navigate = useNavigate()

  const [email, setEmail] = useState("")
  const [emailResult, setEmailResult] = useState<string | null>(null)
  const [challenge, setChallenge] = useState<WebAuthnChallenge | null>(null)

  // only show after initial setup completes, and if there is no access token.
  // also hide if the email auth modal is open.
  const opened = accountStore.initialSetupComplete && !auth.accessToken

  useEffect(() => {
    if (opened && !challenge) {
      newChallenge(accountStore).then((res) => setChallenge(res))
    }
  }, [opened])

  const showEmailAuth = !!loc.state?.showEmailAuth
  const showOptions = !showEmailAuth

  let content

  if (showOptions) {
    content = (
      <SigninOptions
        enabledOptions={{
          email: true,
          guest: true,
        }}
        onSelect={(type) => {
          if (!opened) {
            return Promise.resolve()
          }

          if (type == SigninOptionType.guest) {
            return accountStore
              .createAccount(undefined, challenge ?? undefined)
              .then((res) => {
                if (res === false) {
                  // retry?
                  return newChallenge(accountStore).then((challenge) => {
                    setChallenge(challenge)
                  })
                }
              })
          } else if (type == SigninOptionType.email) {
            // show email auth dialog
            setEmail("")
            navigate(loc, { state: { ...loc.state, showEmailAuth: true } })
          }

          return Promise.resolve()
        }}
      />
    )
  } else if (showEmailAuth) {
    content = (
      <EmailAuth
        email={email || null}
        onSubmit={async (enteredEmail) => {
          if (!opened) {
            return false
          }

          try {
            await accountStore.sendVerificationEmail(enteredEmail)
            setEmail(enteredEmail)
            return true
          } catch (err) {
            if (isWretchError(err) && err.status == 422) {
              return false
            } else {
              throw err
            }
          }
        }}
        onVerify={async (enteredEmail, code) => {
          if (!opened) {
            return false
          }

          const result = await accountStore.verifyEmail(enteredEmail, code)
          if (result) {
            const challenge = await newChallenge(accountStore)
            setChallenge(challenge)
            setEmailResult(result)
            setEmail("")
            return true
          } else {
            return false
          }
        }}
        onComplete={() => {
          return accountStore
            .createAccount(
              { emailToken: emailResult ?? undefined },
              challenge ?? undefined
            )
            .then((res) => {
              if (res === false) {
                // get a new challenge and try again?
                return newChallenge(accountStore).then((challenge) => {
                  setChallenge(challenge)
                })
              } else if (res) {
                navigate(-1)
              } else {
                // other error
              }
            })
        }}
      />
    )
  }

  return <SigninDialog opened={opened}>{content}</SigninDialog>
})

const newChallenge = (accountStore: AccountStore) =>
  accountStore.webAuthnAvailable
    ? accountStore.getWebAuthnRegistrationChallenge()
    : Promise.resolve(null)
