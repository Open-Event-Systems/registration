import {
  ModalDialog,
  ModalDialogProps,
} from "#src/components/dialog/ModalDialog.js"
import { getWebAuthnRegistrationChallenge } from "#src/features/auth/api.js"
import { SigninOptionsMenu } from "#src/features/auth/components/SigninOptionsMenu.js"
import { signInOptions } from "#src/features/auth/signInOptions.js"
import { AuthInfo } from "#src/features/auth/stores/AuthInfo.js"
import { AuthStore } from "#src/features/auth/stores/AuthStore.js"
import {
  SignInComponentProps,
  SignInOption,
  SignInOptions,
} from "#src/features/auth/types/SignInOptions.js"
import { WebAuthnChallenge } from "#src/features/auth/types/WebAuthn.js"
import { useLocation, useNavigate } from "#src/hooks/location.js"
import {
  DefaultProps,
  Selectors,
  createStyles,
  useComponentDefaultProps,
} from "@mantine/core"
import { action, runInAction } from "mobx"
import { observer, useLocalObservable } from "mobx-react-lite"
import { ComponentType, useEffect } from "react"
import { Wretch } from "wretch"

/**
 * The local storage key for the stored credential ID.
 */
const WEBAUTHN_CREDENTIAL_ID_LOCAL_STORAGE_KEY = "oes-credential-id-v1"

declare module "#src/hooks/location.js" {
  interface LocationState {
    signInMethod?: keyof SignInOptions
  }
}

const useStyles = createStyles({
  root: {},
  body: {
    padding: "0 0 8px 0",
  },
  content: {},
})

export type SigninDialogProps = Omit<
  ModalDialogProps,
  "styles" | "fullScreen" | "onClose" | "onSelect"
> &
  DefaultProps<Selectors<typeof useStyles>>

/**
 * Sign in dialog component.
 */
export const SigninDialog = (props: SigninDialogProps) => {
  const { className, classNames, styles, unstyled, title, children, ...other } =
    useComponentDefaultProps(
      "SigninDialog",
      {
        title: "Sign In",
      },
      props
    )

  const { classes, cx } = useStyles(undefined, {
    name: "SigninDialog",
    classNames,
    styles,
    unstyled,
  })

  return (
    <ModalDialog
      className={cx(classes.root, className)}
      title={title}
      classNames={{
        content: classes.content,
        body: classes.body,
      }}
      closeOnClickOutside={false}
      hideCloseButton
      onClose={() => null}
      centered
      {...other}
    >
      {children}
    </ModalDialog>
  )
}

export type SigninDialogManagerProps = {
  authStore: AuthStore
  wretch: Wretch
}

SigninDialog.Manager = observer((props: SigninDialogManagerProps) => {
  const { authStore, wretch } = props
  const navigate = useNavigate()
  const loc = useLocation()

  const state = useLocalObservable(() => ({
    wretch,
    ready: false,
    options: [] as SignInOption[],

    _webAuthnCredentialId: null as string | null,
    get webAuthnCredentialId() {
      return this._webAuthnCredentialId
    },
    set webAuthnCredentialId(value: string | null) {
      this._webAuthnCredentialId = value
      saveWebAuthnCredentialId(value)
    },

    webAuthnRegistrationChallenge: null as WebAuthnChallenge | null,

    _webAuthnError: false,
    get webAuthnError() {
      return this._webAuthnError
    },
    set webAuthnError(value: boolean) {
      this._webAuthnError = value
    },

    _loading: false,
    get loading() {
      return this._loading
    },
    set loading(value: boolean) {
      this._loading = value
    },

    Component: null as ComponentType<SignInComponentProps> | null,

    get isWebAuthnAvailable() {
      return !!this.options.find((opt) => opt.id == "platformWebAuthn")
    },

    async load() {
      this._webAuthnCredentialId = getSavedWebAuthnCredentialId()
      await this.loadOptions()

      if (this.isWebAuthnAvailable) {
        this.webAuthnRegistrationChallenge =
          await getWebAuthnRegistrationChallenge(wretch)
      }

      runInAction(() => {
        this.ready = true
      })
    },
    async loadOptions() {
      const options = await Promise.all(
        Object.values(signInOptions).map((opt) => {
          if (typeof opt === "function") {
            return opt(this)
          } else {
            return opt
          }
        })
      )
      runInAction(() => {
        this.options = options.filter((opt): opt is SignInOption => !!opt)
      })
    },

    handleComplete(authInfo: AuthInfo) {
      authStore.authInfo = authInfo
    },
  }))

  const show = authStore.ready && !authStore.authInfo
  const signInMethod = loc.state?.signInMethod
  const signInOption = state.options.find((opt) => opt.id == signInMethod)

  useEffect(
    action(() => {
      if (show) {
        state.load()
      } else {
        state.ready = false
      }
    }),
    [show]
  )

  useEffect(() => {
    if (
      state.webAuthnCredentialId &&
      state.isWebAuthnAvailable &&
      !state.webAuthnError
    ) {
      // TODO: should choose the available webauthn method... or do this in a cleaner way
      navigate(loc, {
        state: { ...loc.state, signInMethod: "platformWebAuthn" },
      })
    }
  }, [state.ready])

  useEffect(() => {
    if (signInOption) {
      signInOption.factory(state).then(
        action((c) => {
          if (c && !state.Component) {
            state.Component = c
          } else if (!c) {
            // finished without needing a component, go back
            navigate(-1)
          }
        })
      )
    }
  }, [signInOption])

  let content

  if (signInOption && state.Component) {
    content = <state.Component state={state} />
  } else {
    content = (
      <SigninOptionsMenu
        options={state.options}
        onSelect={action((id) => {
          state.Component = null
          navigate(window.location, {
            state: { ...loc.state, signInMethod: id },
          })
        })}
      />
    )
  }

  return (
    <SigninDialog
      opened={show && state.ready}
      loading={state.loading || (!!signInOption && !state.Component)}
    >
      {content}
    </SigninDialog>
  )
})

SigninDialog.Manager.displayName = "SigninDialog.Manager"

/**
 * Get the saved WebAuthn credential ID.
 */
const getSavedWebAuthnCredentialId = () => {
  const id = window.localStorage.getItem(
    WEBAUTHN_CREDENTIAL_ID_LOCAL_STORAGE_KEY
  )
  if (!id || typeof id !== "string") {
    return null
  } else {
    return id
  }
}

/**
 * Save the WebAuthn credential ID.
 */
const saveWebAuthnCredentialId = (credentialId: string | null | undefined) => {
  if (credentialId) {
    window.localStorage.setItem(
      WEBAUTHN_CREDENTIAL_ID_LOCAL_STORAGE_KEY,
      credentialId
    )
  } else {
    window.localStorage.removeItem(WEBAUTHN_CREDENTIAL_ID_LOCAL_STORAGE_KEY)
  }
}
