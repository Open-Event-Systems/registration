import {
  ModalDialog,
  ModalDialogProps,
} from "#src/components/dialog/ModalDialog.js"
import { SigninOptionsMenu } from "#src/features/auth/components/SigninOptionsMenu.js"
import { AccountStore } from "#src/features/auth/stores/AccountStore.js"
import { AuthStore } from "#src/features/auth/stores/AuthStore.js"
import {
  SignInOption,
  SignInOptions,
} from "#src/features/auth/types/SignInOptions.js"
import { WebAuthnChallenge } from "#src/features/auth/types/WebAuthn.js"
import {
  DefaultProps,
  Selectors,
  createStyles,
  useComponentDefaultProps,
} from "@mantine/core"
import { observer, useLocalObservable } from "mobx-react-lite"

const useStyles = createStyles({
  root: {},
  body: {
    padding: "0 0 8px 0",
  },
  content: {},
})

export type SigninDialogProps = {
  options: SignInOption[]
  onSelect?: (id: keyof SignInOptions) => void
} & Omit<
  ModalDialogProps,
  "styles" | "fullScreen" | "onClose" | "onSelect" | "children"
> &
  DefaultProps<Selectors<typeof useStyles>>

/**
 * Sign in dialog component.
 */
export const SigninDialog = (props: SigninDialogProps) => {
  const {
    className,
    classNames,
    styles,
    unstyled,
    title,
    options,
    onSelect,
    ...other
  } = useComponentDefaultProps(
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
      <SigninOptionsMenu options={options} onSelect={onSelect} />
    </ModalDialog>
  )
}

export type SigninDialogManagerProps = {
  authStore: AuthStore
  accountStore: AccountStore
}

SigninDialog.Manager = observer((props: SigninDialogManagerProps) => {
  const { authStore, accountStore } = props

  const state = useLocalObservable(() => ({
    emailToken: null as string | null,
    webAuthnRegistrationChallenge: null as WebAuthnChallenge | null,
    webAuthnAuthenticationChallenge: null as WebAuthnChallenge | null,
  }))

  // TODO: loading and stuff
  return null
})

SigninDialog.Manager.displayName = "SigninDialog.Manager"
